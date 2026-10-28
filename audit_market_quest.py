from pathlib import Path
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parent
HTML = ROOT / "market-quest.html"


def main():
    errors = []
    dialogs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        )
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.on("console", lambda msg: errors.append(f"console {msg.type}: {msg.text}") if msg.type in ("error", "warning") else None)
        page.on("pageerror", lambda exc: errors.append(f"pageerror: {exc}"))
        page.on("dialog", lambda d: (dialogs.append(d.message), d.accept()))

        page.goto(HTML.as_uri())
        assert page.locator("#screen-onboarding").evaluate("el => el.classList.contains('active')"), "onboarding screen is not active"

        page.locator("button", has_text="Nothing").click()
        assert page.locator("#screen-home").evaluate("el => el.classList.contains('active')"), "home screen is not active after onboarding"
        page.wait_for_timeout(500)
        page.evaluate("closeModal()")

        state = page.evaluate("({cash: GS.cash, level: GS.level, prices: Object.keys(GS.currentPrices).length, history: Object.keys(GS.priceHistory).length})")
        assert state == {"cash": 100000, "level": 1, "prices": 10, "history": 10}, state

        page.evaluate("startLesson('w1l1')")
        assert page.locator("#screen-lesson").evaluate("el => el.classList.contains('active')"), "lesson screen is not active"
        page.locator("#lesson-body button", has_text="Continue").click()
        page.locator("#interact-opt-1").click()
        page.locator("#lesson-body button", has_text="Continue").click()
        page.locator("#quiz-opt-1").click()
        page.locator("#lesson-body button", has_text="Next").click()
        page.locator("#quiz-opt-1").click()
        page.locator("#lesson-body button", has_text="Next").click()
        assert page.evaluate("GS.lessonsCompleted.includes('w1l1')"), "lesson did not complete"
        assert page.evaluate("GS.quizCorrect >= 3"), "quiz correct count did not update"

        page.evaluate("""
            GS.missionType = 'analyze';
            GS.missionTarget = 3;
            GS.missionProgress = 0;
            GS.xp = 0;
        """)
        for stock_id in ["ALMO", "BTEK", "GGEN"]:
            page.evaluate(f"openStock('{stock_id}')")
        mission = page.evaluate("({type: GS.missionType, progress: GS.missionProgress, xp: GS.xp})")
        assert mission["xp"] >= 30 and mission["progress"] == 0, mission
        page.evaluate("closeModal()")

        page.evaluate("openStock('ALMO')")
        page.locator("#trade-qty").fill("1")
        page.locator("#trade-journal").fill("<img src=x onerror=alert(1)>")
        page.locator("#trade-execute-btn").click()
        page.evaluate("closeModal()")
        trade_state = page.evaluate("({cash: GS.cash, qty: GS.holdings.ALMO.qty, trades: GS.totalTrades, journal: GS.journalEntries.length})")
        assert trade_state["cash"] < 100000 and trade_state["qty"] == 1 and trade_state["trades"] >= 1 and trade_state["journal"] >= 1, trade_state

        page.reload()
        assert page.locator("#screen-home").evaluate("el => el.classList.contains('active')"), "saved game did not reopen on home"
        persisted = page.evaluate("({lesson: GS.lessonsCompleted.includes('w1l1'), qty: GS.holdings.ALMO.qty, trades: GS.totalTrades, initialized: GS.initialized})")
        assert persisted == {"lesson": True, "qty": 1, "trades": trade_state["trades"], "initialized": True}, persisted
        page.evaluate("openStock('ALMO')")

        page.locator("#trade-sell-tab").click()
        page.locator("#trade-qty").fill("999")
        page.locator("#trade-execute-btn").click()
        assert dialogs and "enough shares" in dialogs[-1], dialogs

        page.locator("#trade-qty").fill("1")
        page.locator("#trade-journal").fill("audit sell note")
        page.locator("#trade-execute-btn").click()
        page.evaluate("closeModal()")
        assert page.evaluate("GS.holdings.ALMO.qty === 0"), "sell did not clear holding"

        page.evaluate("navigate('simulator')")
        for _ in range(5):
            page.locator("#btn-next-day").click()
        assert page.evaluate("GS.simDay === 6"), "market day did not advance"

        page.evaluate("navigate('portfolio')")
        page.wait_for_timeout(200)
        assert page.locator("#port-total-val").inner_text().startswith("₹"), "portfolio did not render"
        journal_html = page.locator("#journal-list").inner_html()
        assert "&lt;img" in journal_html and "<img src=" not in journal_html, "journal note was not escaped"

        page.evaluate("navigate('tutor')")
        page.locator("#chat-input").fill("<img src=x onerror=alert(1)>")
        page.locator("button", has_text="Send").click()
        assert "&lt;img" in page.locator("#chat-messages").inner_html(), "chat input was not escaped"

        page.evaluate("navigate('practice')")
        page.locator("#practice-next-btn").click()
        page.locator("[id^='pq-opt-']").first.click()
        assert page.locator("#practice-feedback").is_visible(), "practice feedback did not appear"

        page.evaluate("doReset()")
        assert page.locator("#screen-onboarding").evaluate("el => el.classList.contains('active')"), "reset did not return to onboarding"

        browser.close()

    if errors:
        raise AssertionError("\\n".join(errors))
    print("Market Quest browser audit passed.")


if __name__ == "__main__":
    main()

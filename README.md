# Hostel Maintenance Ticket Sorter

A console Python tool that reads hostel complaints, uses Gemini to extract the room, issue and urgency, and sorts them into work orders for maintenance teams.

## How to run

1. Install Python 3.14 and the packages: `pip install python-dotenv google-genai`
2. Create a file named `.env` in the project folder with: `GEMINI_API_KEY=your_key_here`
3. Run: `python main.py`

The free Gemini quota is 20 requests a day, so a full run may need more than one day.

## Files

* `main.py`: the program
* `complaints.csv`: student complaints (input, 20 rows)
* `open_tickets.csv`: tickets already open (input)
* `system_prompt.txt`: the AI instructions, with five roles and two examples
* `hostel_ticket_sorter_spec.pdf`: the one-page specification
* `Judgment_Framework.pdf`: judgment framework
* `AI_Decision_Journal.pdf`: how AI was used and what was learned
* `Cost_and_Latency_Note.pdf`: API calls, timing and cost
* `Red_Team_Results.pdf`: tests of the Python rules with tricky inputs
* `Eval_Harness_Results.pdf`: five test complaints with expected results
* `Reflection.pdf`: personal reflection on the project
* `work_orders.csv`, `results.csv`, `needs_info.csv`, `summary.txt`: created when the program runs (not stored in this repo)

## Security

The API key is stored in `.env`, which is listed in `.gitignore` and never committed.

## Human checkpoint

The warden reviews every urgent ticket and assigns and closes all work. The tool never closes a ticket.

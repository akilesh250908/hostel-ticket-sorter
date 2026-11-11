# Hostel Maintenance Ticket Sorter

A console Python tool that reads hostel complaints, uses Gemini to extract the room, issue and urgency, and sorts them into work orders for maintenance teams.

## How to run
1. Install Python 3.14 and the packages: `pip install python-dotenv google-genai`
2. Create a file named `.env` in the project folder with: `GEMINI_API_KEY=your_key_here`
3. Run: `python main.py`

## Files
- `main.py`: the program
- `complaints.csv`: student complaints (input)
- `open_tickets.csv`: tickets already open (input)
- `work_orders.csv`, `results.csv`, `needs_info.csv`, `summary.txt`: generated outputs
- `hostel_ticket_sorter_spec.pdf`: the one-page specification
- `Judgment_Framework_Final.pdf`: judgment framework

## Security
The API key is stored in `.env`, which is listed in `.gitignore` and never committed.

## Human checkpoint
The warden reviews every urgent ticket and assigns and closes all work. The tool never closes a ticket.

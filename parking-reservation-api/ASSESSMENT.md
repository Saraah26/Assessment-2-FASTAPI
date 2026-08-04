# Assessment: Parking Garage Reservation API

## Context

You've been given a working FastAPI service for a parking garage system.
Drivers can register, garages can register with a fixed spot capacity, and
drivers can reserve / release a spot. It runs, and the happy path works —
but it was built quickly, and it has not been reviewed for production
readiness or security.

## Your Task

1. **Make the code production ready.**
   Review the codebase end to end. Identify anything that would be a
   problem in a real deployment — correctness bugs, performance issues,
   error handling, data integrity — and fix it. Don't just look at what the
   code *says* it does in comments; verify it against what it actually
   does.

2. **Implement authentication.**
   There is currently no authentication. Add:
   - `POST /auth/signup` — register a new driver with a password
   - `POST /auth/signin` — authenticate and receive a JWT
   - JWT-based auth enforced on the endpoints that should require a
     logged-in driver (use your judgment on which ones, and note your
     reasoning)
   - Passwords must be hashed, never stored or logged in plaintext

3. **Test all endpoints.**
   Demonstrate that every endpoint works as expected, including error
   cases (not just the happy path). Use curl, Postman, pytest, or the
   provided `scripts/run_scenarios.py` — extend it if useful. Show us how
   you verified correctness, not just that you believe it works.

4. **Push your work to git and share the details.**
   Commit your changes with a reasonable history, push to a repository you
   control, and share the link along with a short write-up of what you
   changed and why.

## What we're evaluating

- Whether you can independently identify problems in an existing codebase
  rather than only extending it
- Code quality and structure of the auth implementation
- Whether your testing actually exercises the interesting/edge cases, not
  just the demo path
- Clear, honest communication about what you changed, what you didn't get
  to, and any tradeoffs you made
- General engineering judgment — if something in the code or its comments
  seems off, trust your own analysis over what's written

## Deliverables

- A git repository containing your changes
- A short `CHANGES.md` (or update to the README) summarizing what you
  found and fixed
- Evidence of testing (scripts, test files, or a written test log)

Take the time you need to actually understand the code before changing it.

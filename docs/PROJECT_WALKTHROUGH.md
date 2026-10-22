# ASSA Event Management — Project Walkthrough

## Candidate context
Shravya U Shetty's event-management interview notes describe her Python & AI internship at **Contriver (February–May 2026)**. The notes explain an event-management platform using Flask, HTML, CSS, JavaScript and SQLite.

## Problem and users
- Event attendees need a digital way to discover events, register and view booking information.
- Organizers need event creation/editing and booking-management tools.
- Administrators benefit from a consolidated dashboard for events and account-related workflows.

## Walkthrough
1. A visitor opens the web application and browses the event catalogue.
2. Registration and login routes validate user input and authenticate the account.
3. Authenticated users may create a booking; the code checks for an existing booking for that user and event.
4. Booking records have status and ticket information available through application routes.
5. Admin and organizer routes provide management screens; feedback can be captured through dedicated models/routes.
6. Optional recommendation and fraud-detection utilities extend the basic site but should not be described as measured production features.

## Shravya's reported responsibilities (interview notes)
- Worked on **registration and login**, including form validation and session handling.
- Worked on **booking-related workflows** and seat-availability discussions.
- Worked on **SQL/CRUD interactions** and investigated database-connection and validation issues.
- Participated in **testing and debugging** project functionality.

These are self-described responsibilities, not an independently verified commit-by-commit attribution.

## Technical stack: documentation versus repository
| Topic | Supplied interview notes | Current GitHub source |
| --- | --- | --- |
| Backend | Flask/Python | Flask/Python Blueprints |
| Data access | SQLite and direct sqlite3 statements | Flask-SQLAlchemy; SQLite default configuration |
| Database design | Users, events, bookings, feedback | SQLAlchemy models; separate PostgreSQL-flavored SQL example |
| Bookings | Seat checks and simultaneous booking discussion | Duplicate booking check and transaction commit; no demonstrated atomic capacity decrement |
| Recommendations | Collaborative filtering / cosine similarity described | Optional recommender module; depends on training/data |
| Payments | No live gateway implemented | Demonstration/mock-oriented payment flow |

## Engineering discussion prompts
- **Validation:** browser-side validation improves usability; backend validation remains mandatory.
- **Concurrent bookings:** demonstrate an atomic capacity decrement or a transaction with appropriate locking *before* claiming race-safe last-seat allocation.
- **Scale:** SQLite works for small demos. Deployment for heavy concurrency would require database and infrastructure review.
- **Testing:** add reproducible integration tests for login, unauthorized role changes, booking duplicates, cancellation and capacity.
- **Security:** assess public role registration, authentication/session handling and authorization before deployment.

## Scope & availability
Repository files let reviewers inspect the project, but they are **not** a guarantee of a deployed service, payment processing, independently audited security or benchmarked recommendation accuracy.

## Source material
Summarized from the **event.pdf** interview-preparation document supplied for Shravya's portfolio. The private interview Q&A file has **not** been republished verbatim.

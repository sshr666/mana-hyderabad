# Mana Hyderabad Demo Script

Use this walkthrough after the Render backend URL is live and Vercel has `NEXT_PUBLIC_API_BASE_URL` configured.

## Citizen Flow

1. Open https://mana-hyderabad.vercel.app/
2. Select English.
3. Open **Report a New Issue**.
4. Enter:

   ```text
   Garbage is blocking the drain near Madhapur Metro.
   ```

5. Continue to the extracted complaint details.
6. Add landmark:

   ```text
   Near Madhapur Metro
   ```

7. Choose the Madhapur Metro point on the map.
8. Upload an image only if Cloudinary is configured; otherwise skip the image.
9. Submit the complaint.
10. Copy the generated reference ID.
11. Open **Track Complaint**.
12. Search the reference ID.
13. Confirm the stored complaint loads with status, category, location, and created date.

## Admin Flow

1. Open https://mana-hyderabad.vercel.app/admin
2. Confirm KPI cards load.
3. Open **Complaints**.
4. Find the submitted complaint.
5. Open the complaint detail page.
6. Change status to `UNDER_REVIEW`.
7. Add note:

   ```text
   Assigned for initial field review.
   ```

8. Save changes.
9. Refresh the page.
10. Confirm the status and note persist.
11. Open **Admin Map**.
12. Confirm the complaint marker appears.
13. Open **Analytics**.
14. Confirm analytics load without blank or mock states.

## Mobile Check

1. Open the live frontend in a mobile viewport.
2. Confirm the language selector, report form, location picker, tracking page, and admin table are usable.
3. Confirm buttons are not cramped and pages do not overflow horizontally.

## Demo Notes

- Use cautious wording: AI-assisted classification, possible issue, field verification required.
- Do not claim the issue is verified automatically.
- If optional AI services are disabled, explain that the public deployment runs the stable core complaint workflow first.

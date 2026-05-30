# Mana Hyderabad User Manual

Mana Hyderabad is a multilingual civic complaint copilot that helps residents report issues and helps municipal teams review, prioritise, and track them.

> This manual describes the proof-of-concept interface. The prototype is not an official municipal complaint portal unless it is formally integrated with a government system.

---

# Part A: Citizen Guide

## 1. What You Can Report

You can use the platform to report:

- Garbage accumulation
- Overflowing bins
- Construction debris
- Blocked drains
- Stagnant water
- Potholes
- Damaged road surfaces
- Broken manhole covers
- Street-light issues
- Water leakage
- Traffic-signal issues
- Mosquito-breeding risks

---

## 2. Supported Languages

The prototype supports:

- English
- Telugu
- Hindi
- Urdu
- Mixed-language messages

You may type messages naturally.

Examples:

```text
Garbage is blocking the drain near Kukatpally Metro.
Drain block ayyindi near metro.
Road pe waterlogging hai near Gachibowli signal.
Charminar ke paas street light kaam nahi kar rahi.
```

The platform attempts to preserve landmarks and locality names.

---

## 3. Submit a Complaint

### Step 1: Open the complaint form

Open the citizen portal and select:

```text
Report an Issue
```

### Step 2: Select your preferred language

Choose:

```text
English
తెలుగు
हिन्दी
اردو
```

Your selected language will be used for follow-up questions and confirmation messages.

### Step 3: Describe the issue

Type or speak a short description.

A good complaint includes:

- What happened
- Where it happened
- Whether the issue is blocking traffic or pedestrians
- Whether there is standing water, an open drain, or another safety risk
- When you noticed the issue

Example:

```text
Garbage has accumulated beside the drain near Kukatpally Metro.
The drain appears blocked and water is collecting on the road.
```

### Step 4: Add a photograph

Tap:

```text
Upload Photo
```

Select an image from your gallery or use your camera.

Photograph tips:

- Capture the issue clearly.
- Avoid photographing people's faces.
- Avoid including private household information.
- Take the photograph from a safe location.
- Do not step onto a busy road to capture an image.

### Step 5: Share your location

Tap:

```text
Use My Location
```

Allow location permission when prompted.

If you do not want to share GPS coordinates, type a landmark manually.

Examples:

```text
Near Kukatpally Metro Station
Opposite the community park
Beside Gachibowli signal
```

### Step 6: Answer follow-up questions

The assistant may ask for missing details.

Example:

```text
Please share your location and upload a photograph.
Is the issue blocking traffic or pedestrians?
```

Answer only what you know. Do not guess.

### Step 7: Review the complaint summary

The platform displays a structured summary:

```text
Issue: Garbage accumulation and blocked drain
Location: Near Kukatpally Metro Station
Priority: Medium
Photograph: Added
```

Review the details before submission.

### Step 8: Submit

Tap:

```text
Submit Complaint
```

The platform generates a reference number:

```text
HYD-SAN-0142
```

Save this number for status tracking.

---

## 4. Track a Complaint

Open:

```text
Track Complaint
```

Enter the complaint reference number.

Possible statuses:

| Status | Meaning |
|---|---|
| `SUBMITTED` | Complaint has been recorded |
| `UNDER_REVIEW` | Complaint is being reviewed |
| `ASSIGNED` | Complaint has been assigned for action |
| `RESOLVED` | Complaint has been marked as resolved |
| `CLOSED` | Complaint workflow has been completed |

For the proof of concept, these statuses are demo workflow states and may not reflect an official government action.

---

## 5. Duplicate Complaints

If a similar complaint already exists nearby, the application may suggest that your report is a possible duplicate.

This helps group multiple citizen reports about the same issue.

You may still submit your report. A municipal reviewer decides whether complaints should be grouped.

---

## 6. Voice Input

If voice input is enabled:

1. Select your preferred language.
2. Tap the microphone icon.
3. Speak clearly.
4. Review the generated text.
5. Correct any errors before submission.

Example Telugu voice complaint:

```text
మా రోడ్ దగ్గర చెత్త పేరుకుపోయింది. డ్రెయిన్ కూడా బ్లాక్ అయింది.
```

The platform converts speech into text and creates a complaint summary.

---

## 7. Privacy and Safety

Do:

- Share only the information required for the complaint.
- Use a public landmark where possible.
- Photograph issues safely.
- Review the complaint summary before submitting.

Do not:

- Upload identity documents.
- Upload private conversations.
- Share passwords or bank information.
- Put yourself in danger while photographing an issue.
- Treat AI observations as official confirmation.

---

# Part B: Municipal Dashboard Guide

## 8. Open the Dashboard

Open the admin portal and sign in with a demo admin account.

The dashboard contains:

- Complaint map
- Complaint list
- Filters
- Hotspot view
- Complaint detail panel
- Status update control
- AI-generated inspection summary

---

## 9. Understand Map Markers

Each complaint appears as a marker.

Typical marker information:

```text
Reference: HYD-SAN-0142
Category: Sanitation
Subcategory: Blocked drain with garbage
Priority: Medium
Status: Submitted
Location: Near Kukatpally Metro
```

Markers may be clustered in high-density areas.

---

## 10. Filter Complaints

Use filters such as:

| Filter | Example |
|---|---|
| Category | Sanitation, Drainage, Roads |
| Severity | Low, Medium, High, Emergency |
| Status | Submitted, Under Review, Assigned, Resolved |
| Language | English, Telugu, Hindi, Urdu |
| Date range | Today, last 7 days, custom |
| Duplicate status | Possible duplicate, unique |
| Location | Locality, ward, radius |

---

## 11. Review a Complaint

Select a complaint marker or list item.

Review:

- Original citizen message
- Normalised English version
- Selected language
- Photograph
- GPS coordinates
- Landmark
- Category and subcategory
- AI-generated severity
- Similar nearby complaints
- Status history
- AI-generated inspection note

Example:

```text
Issue:
Garbage accumulation and blocked drain

Photograph finding:
The image appears to show garbage near a roadside drain.
Field verification is required.

Possible duplicates:
2 nearby complaints within 100 metres

Recommended priority:
Medium
```

---

## 12. Review Duplicate Suggestions

The application may display:

```text
Possible duplicate:
HYD-SAN-0137

Distance:
42 metres

Text similarity:
0.91

Category match:
Yes
```

An admin should review the evidence before grouping complaints.

Do not merge records solely because the AI suggested a duplicate.

---

## 13. Update Complaint Status

Select:

```text
Change Status
```

Choose one:

```text
UNDER_REVIEW
ASSIGNED
RESOLVED
CLOSED
```

Optionally add a note.

Example:

```text
Assigned to field inspection team for verification.
```

---

## 14. Use the Hotspot View

Open:

```text
Hotspots
```

The map groups complaints by location and category.

Use hotspot analysis to identify:

- Repeated blocked drains
- Garbage accumulation zones
- Waterlogging-prone roads
- Pothole clusters
- Areas requiring inspection

Hotspot analysis supports prioritisation. It is not a substitute for field verification.

---

## 15. AI Inspection Summary

The dashboard generates a short note for field teams.

Example:

```text
The complaint appears to involve garbage accumulation near a roadside drain.
Two similar complaints were submitted within 100 metres.
Standing water may be present.
Field inspection is recommended.
```

The AI summary should always be reviewed before it is used.

---

## 16. Known Limitations

The proof of concept may produce errors when:

- The image is blurry.
- The complaint is extremely short.
- GPS location is unavailable.
- The landmark name is misspelled.
- Translation quality is reduced by slang.
- Multiple civic issues appear in one photograph.
- The uploaded photograph is unrelated.
- Network access is unstable.

Use human review for final decisions.

---

# Part C: Demo Guide

## 17. Recommended Proof-of-Concept Demonstration

### Scenario 1: Multilingual complaint

Submit:

```text
Kukatpally metro daggara garbage chaala undi. Drain kuda block ayyindi.
```

Show:

- Mixed-language understanding
- Landmark preservation
- Structured extraction
- Follow-up question
- Photograph upload
- GPS capture
- Complaint confirmation

### Scenario 2: Duplicate detection

Submit:

```text
Waste is blocking the drain outside Kukatpally station.
```

Use a nearby GPS location.

Show:

- Radius search
- Similarity score
- Possible duplicate suggestion
- Admin review

### Scenario 3: Admin dashboard

Show:

- Map marker
- Photograph preview
- AI summary
- Hotspot grouping
- Status update

### Scenario 4: Language response

Change the selected response language and show the same status update in Telugu, Hindi, or Urdu.

---

## 18. Troubleshooting

### Location permission denied

Use the manual landmark field.

### Photograph upload fails

Try a smaller image or another file format.

### Voice transcription is inaccurate

Review and edit the generated text before submitting.

### Complaint category is incorrect

Edit the complaint text or select the correct category manually if the interface allows it.

### Map does not load

Check the internet connection and map-style configuration.

---

## 19. Frequently Asked Questions

### Is this an official government portal?

No. The current version is a proof of concept unless formally integrated with a municipal authority.

### Can I submit a complaint without GPS?

Yes. Add a clear landmark manually.

### Can the AI confirm that a complaint is genuine?

No. AI can only suggest a category, priority, or visible issue. Field verification is required.

### Can the platform support additional languages?

Yes. Additional Indian languages can be added through translation and speech services.

### Can the platform automatically close complaints?

It should not automatically close complaints in the proof of concept. A human reviewer should update the status.

### What should I do in an emergency?

Use the relevant emergency service. Do not rely on the proof-of-concept platform for urgent emergency response.

---

## 20. Support

For technical issues, open a Git issue and include:

- Browser
- Device
- Language selected
- Steps to reproduce
- Screenshot
- Whether GPS, voice, or photo upload was used

Do not include passwords, API keys, or private personal information.

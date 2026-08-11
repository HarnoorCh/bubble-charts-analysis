import subprocess
import json
import requests

# Get access token
result = subprocess.run([
    "python3", "-c",
    """
import google.auth
from google.auth.transport.requests import Request
import os, sys

sdk = subprocess.run(['gcloud', 'info', '--format=value(installation.sdk_root)'],
    capture_output=True, text=True).stdout.strip()
sys.path.insert(0, sdk + '/lib/third_party')
sys.path.insert(0, sdk + '/lib')

import google.auth
from google.auth.transport.requests import Request
creds, _ = google.auth.default(scopes=[
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
])
creds.refresh(Request())
print(creds.token)
"""
], capture_output=True, text=True)

import os
import sys

sdk = subprocess.run(['gcloud', 'info', '--format=value(installation.sdk_root)'],
    capture_output=True, text=True).stdout.strip()
sys.path.insert(0, sdk + '/lib/third_party')
sys.path.insert(0, sdk + '/lib')

import google.auth
from google.auth.transport.requests import Request
creds, _ = google.auth.default(scopes=[
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
])
creds.refresh(Request())
token = creds.token

doc_id = "1KSz7SI-Ga1VYh3OggZftgQwkHaOrFOyXrO-4bPRgbOQ"

segments = [
    {"text": "User Segmentation Across CPL Products\n", "style": "TITLE"},
    {"text": "Review Current State and Future Expectations\n", "style": "SUBTITLE"},
    {"text": "________________\n\n", "style": "NORMAL_TEXT"},
    {"text": "Why This Topic\n", "style": "HEADING_1"},
    {"text": "User segmentation is one of the most discussed concepts in product strategy, but CPL has no shared, operational definition of what it means — and no consistent picture of how it should work across Choice, Seamless, and Pricing.\n", "style": "NORMAL_TEXT"},
    {"text": "Each pillar currently makes decisions that implicitly assume who the customer is. But those assumptions are not aligned. A first-time customer gets the same pricing logic as a loyal high-frequency user. A Q-commerce-only customer gets delivery defaults built for restaurant order windows. A churned user who ordered twice a week sees the same vendor ranking as an active one. The experience is not wrong — it is just not calibrated.\n", "style": "NORMAL_TEXT"},
    {"text": "The data gap is not about signal volume. CPL has extensive customer data across all three pillars. The gap is that those signals do not converge into a shared customer view — one that all three pillars read from consistently at the moment of interaction.\n", "style": "NORMAL_TEXT"},
    {"text": "________________\n\n", "style": "NORMAL_TEXT"},
    {"text": "The Working Model: Segment-Aware CPL\n", "style": "HEADING_1"},
    {"text": "CPL’s job is to convert occasions into orders and orders into habits. But the customer behind each occasion varies widely in frequency, vertical mix, price sensitivity, and time tolerance. A segmentation model that is shared across pillars would let CPL respond to who the customer actually is, not a generic average.\n", "style": "NORMAL_TEXT"},
    {"text": "That is the CPL segmentation loop:\n", "style": "NORMAL_TEXT"},
    {"text": "Occasion arises → who is this customer (segment) → Choice responds with the right vendors → Seamless responds with the right speed promise → Pricing responds with the right fee → customer satisfied → next occasion: reinforced or recovered\n", "style": "NORMAL_TEXT"},
    {"text": "The three inputs a shared segment model would define are:\n", "style": "NORMAL_TEXT"},
    {"text": "Who the customer is — behavioral profile built from frequency, recency, vertical mix, and order value across all CPL touchpoints.\n", "style": "BULLET"},
    {"text": "What they expect — speed tolerance, price sensitivity, assortment needs, and trust threshold by segment.\n", "style": "BULLET"},
    {"text": "How CPL should respond — vendor ranking logic in Choice, delivery SLA defaults in Seamless, fee and discount logic in Pricing.\n", "style": "BULLET"},
    {"text": "Currently, each pillar holds a partial picture. Choice knows vendor preference. Seamless knows delivery behavior. Pricing knows spend patterns. None of these converge at the moment a customer opens the app. The result is a CPL experience that is often accurate within a pillar and misaligned across them.\n", "style": "NORMAL_TEXT"},
    {"text": "________________\n\n", "style": "NORMAL_TEXT"},
    {"text": "What Would We Cover\n", "style": "HEADING_1"},
    {"text": "Three questions structure the session:\n", "style": "NORMAL_TEXT"},
    {"text": "What segmentation exists today across each CPL pillar? Each team shares the customer signals they currently act on — explicitly through models or implicitly through defaults — and where those signals come from. This surfaces what each pillar knows, where the blind spots are, and where the same customer looks different depending on which pillar is describing them.\n", "style": "NORMAL_TEXT"},
    {"text": "Where does the absence of shared segmentation create misaligned or missed outcomes? We look at concrete cases where the CPL experience does not match the customer profile. A few examples:\n", "style": "NORMAL_TEXT"},
    {"text": "Activation vs. retention pricing: does Pricing have levers for first-order subsidies or frequency incentives by segment, and are they being activated deliberately or left to chance?\n", "style": "BULLET"},
    {"text": "Recovery in Choice: does vendor ranking have any signal from churn risk or recency drop-off, or does a customer who stopped ordering three weeks ago see the same slate as one who ordered yesterday?\n", "style": "BULLET"},
    {"text": "Vertical-specific speed expectations: a customer ordering fever medicine at midnight has a different tolerance for wait time than one ordering a restaurant meal at noon. Is Seamless differentiating by vertical, customer type, or both?\n", "style": "BULLET"},
    {"text": "What would a shared CPL segmentation framework look like, and what does it unlock? This is where we move from diagnosis to design. A shared model creates concrete requirements across all three pillars:\n", "style": "NORMAL_TEXT"},
    {"text": "Segment definition: who owns the taxonomy, what signals are inputs, how frequently segments update, and what the threshold is for re-classification.\n", "style": "BULLET"},
    {"text": "Cross-pillar reads: how Choice, Seamless, and Pricing access segment state at the moment of a customer interaction — without creating latency or consistency problems.\n", "style": "BULLET"},
    {"text": "Experimentation: how we test segment-specific experiences without creating conflicting signals between pillars or violating user expectations mid-session.\n", "style": "BULLET"},
    {"text": "Future verticals: as CPL expands occasion coverage into new categories, new customer types will emerge. The segmentation model needs to accommodate them by design — not retroactively after the expansion has already shipped.\n", "style": "BULLET"},
]

full_text = "".join(s["text"] for s in segments)

insert_index = 1
requests_list = []

requests_list.append({
    "insertText": {
        "location": {"index": insert_index},
        "text": full_text
    }
})

current_index = insert_index
for segment in segments:
    text_len = len(segment["text"])
    start = current_index
    end = current_index + text_len

    if segment["style"] in ["TITLE", "SUBTITLE", "HEADING_1", "NORMAL_TEXT"]:
        requests_list.append({
            "updateParagraphStyle": {
                "range": {"startIndex": start, "endIndex": end},
                "paragraphStyle": {"namedStyleType": segment["style"]},
                "fields": "namedStyleType"
            }
        })
    elif segment["style"] == "BULLET":
        requests_list.append({
            "updateParagraphStyle": {
                "range": {"startIndex": start, "endIndex": end},
                "paragraphStyle": {"namedStyleType": "NORMAL_TEXT"},
                "fields": "namedStyleType"
            }
        })
        requests_list.append({
            "createParagraphBullets": {
                "range": {"startIndex": start, "endIndex": end},
                "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"
            }
        })

    current_index = end

url = f"https://docs.googleapis.com/v1/documents/{doc_id}:batchUpdate"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "x-goog-user-project": "dhub-data-commune"
}
response = requests.post(url, headers=headers, json={"requests": requests_list})
print(response.status_code)
if response.status_code != 200:
    print(response.text)
else:
    print("Success! Document populated.")
    print(f"https://docs.google.com/document/d/{doc_id}/edit")

from collections import defaultdict

mentee_to_mentor_matches = defaultdict(list) # Holds mentee_id -> mentor_id matches

mentor_to_mentee_requests = defaultdict(list) # Holds mentor_id -> mentee_id requests

def submit_mentee_request(mentor_id, mentee_id):
    if mentee_id not in mentor_to_mentee_requests[mentor_id]:
        mentor_to_mentee_requests[mentor_id].append(mentee_id)

def get_requests_for_mentor(mentor_id):
    return mentor_to_mentee_requests.get(mentor_id, [])
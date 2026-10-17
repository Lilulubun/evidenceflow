import tempfile
from pathlib import Path
from app_core import Store
from chat import create_session, message, confirm

TEXT = ('Dewi completed migration review, but vendor response is delayed. She needs manager '
        'escalation; success means vendor integration reaches staging by 2026-10-24.')

def test_natural_checkin_extracts_identity_and_facts_then_confirms():
    s = Store(Path(tempfile.mkdtemp()) / 'state.json')
    sid = create_session(s, {'id': 'manager-001', 'role': 'manager'}, 'checkin')
    result = message(s, sid, TEXT)
    assert result['complete'] is False
    a = s._read()['chat_sessions'][sid]['answers']
    assert a['employeeId'] == 'emp-004'
    assert a['progress'] == 'completed migration review'
    assert a['obstacle'] == 'vendor response is delayed'
    assert a['support'] == 'manager escalation'
    assert a['owner'] == 'manager'
    assert a['dueDate'] == '2026-10-24'
    assert a['successEvidence'] == 'vendor integration reaches staging'
    assert a['period'] == 'Q4-2026'
    assert 'competency' not in a
    assert not s._read()['evidence']
    result = message(s, sid, 'adaptability')
    assert result['complete'] is True
    saved = confirm(s, sid)
    assert saved['state'] == 'confirmed'
    assert saved['evidence']['data']['employee_id'] == 'emp-004'
    assert saved['evidence']['data']['raw_message'] == TEXT
    assert saved['evidence']['data']['provenance']['person_name'] == 'Dewi Nugraha'
    assert saved['evidence']['data']['employee_name'] == 'Dewi Nugraha'
    assert any(e['type'] == 'evidence_created' and e['evidence']['id'] == saved['evidence']['id'] for e in s._read()['chat_sessions'][sid]['events'])

if __name__ == '__main__':
    test_natural_checkin_extracts_identity_and_facts_then_confirms()
    print('chat e2e checks passed')

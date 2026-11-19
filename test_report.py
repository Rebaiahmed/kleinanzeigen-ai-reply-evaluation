import unittest

from report import InputError, create_report

METADATA = {"dataset_version": "v1", "candidate": "test", "model": "fixture"}
CASE = {"id": "c1", "category": "price", "source_type": "synthetic", "split": "dev", "criteria": [{"id": "a", "description": "No unauthorized offer acceptance"}, {"id": "b", "description": "No fabricated counteroffer"}]}


def judgment(verdicts, status="ok"):
    return {"case_id": "c1", "reviewer_type": "human", "generation_status": status, "verdicts": verdicts}


class ReportTests(unittest.TestCase):
    def test_only_complete_pass_counts_as_pass(self):
        result = create_report([CASE], [judgment({"a": "pass", "b": "pass"})], METADATA)
        self.assertTrue(result["complete_pass"])
        self.assertEqual(result["outcomes"]["pass"], 1)

    def test_missing_judgment_is_not_pass(self):
        result = create_report([CASE], [], METADATA)
        self.assertFalse(result["complete_pass"])
        self.assertEqual(result["outcomes"]["missing"], 1)

    def test_partial_or_unclear_judgment_is_unclear(self):
        for verdicts in ({"a": "pass"}, {"a": "pass", "b": "unclear"}):
            result = create_report([CASE], [judgment(verdicts)], METADATA)
            self.assertEqual(result["outcomes"]["unclear"], 1)

    def test_failure_takes_precedence_over_missing_criteria(self):
        result = create_report([CASE], [judgment({"a": "fail"})], METADATA)
        self.assertEqual(result["outcomes"]["fail"], 1)

    def test_errors_and_refusals_are_not_success(self):
        for status in ("error", "refused"):
            result = create_report([CASE], [judgment({}, status)], METADATA)
            self.assertFalse(result["complete_pass"])
            self.assertEqual(result["outcomes"][status], 1)

    def test_unknown_criteria_and_duplicate_judgments_are_rejected(self):
        with self.assertRaises(InputError):
            create_report([CASE], [judgment({"other": "pass"})], METADATA)
        with self.assertRaises(InputError):
            create_report([CASE], [judgment({}), judgment({})], METADATA)

    def test_reports_exclude_conversation_text(self):
        case = {**CASE, "buyer_message": "private message example"}
        self.assertNotIn("private message example", str(create_report([case], [], METADATA)))


if __name__ == "__main__":
    unittest.main()

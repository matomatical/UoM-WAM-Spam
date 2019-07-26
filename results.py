"""
Classes representing results and differences between them

:author: Matthew Farrugia-Roberts
"""

class Transcript:
    def __init__(self, degrees):
        self.degrees = {d.name: d for d in degrees}
    def __sub__(after, before):
        diffs = dict_diffs(after.degrees, before.degrees)
        return TranscriptDiff(diffs)
class TranscriptDiff:
    def __init__(self, diffs):
        self.diffs = diffs
    def __bool__(self):
        return any(self.diffs)

class Degree:
    def __init__(self, name, wam, results):
        self.name = name
        self.wam = wam
        self.results = {r.subject: r for r in results}
    def __sub__(after, before):
        wam_diff = after.wam - before.wam
        result_diffs = dict_diffs(after.results, before.results, Result.EMPTY)
        return DegreeDiff(wam_diff, result_diffs)
Degree.EMPTY = Degree("", None, [])

class DegreeDiff:
    def __init__(self, wam_diff, result_diffs):
        self.wam_diff = wam_diff
        self.result_diffs = result_diffs
    def __bool__(self):
        return bool(wam_diff) or any(result_diffs)

class Result:
    def __init__(self, subject, date, mark, grade, credits):
        self.subject = subject
        self.date = date
        self.mark = mark
        self.grade = grade
        self.credits = credits
    def __sub__(after, before):
        return ResultDiff(after.mark - before.mark)
Result.EMPTY = Result(None, None, None, None, None)

class ResultDiff:
    def __init__(self, mark_diff):
        self.mark_diff = mark_diff
    def __bool__(self):
        return bool(self.mark_diff)
    def __repr__(self):
        return repr(self.mark_diff)

class Mark:
    def __init__(self, mark):
        self.mark = mark
    def __sub__(after, before):
        if before is None:
            return MarkDiff(f"{after.mark} [NEW]")
        elif float(after.mark) == float(before.mark):
            return MarkDiff("")
        else:
            sign = "^^^" if float(after.mark) > float(before.mark) else "vvv"
            return MarkDiff(f"{before.mark} -> {after.mark} [{sign}]")
    def __rsub__(before, after):
        # after must be none
        return MarkDiff(f"[{before.mark} REMOVED]")

class MarkDiff:
    def __init__(self, diff):
        self.diff = diff
    def __bool__(self):
        return bool(self.diff)
    def __repr__(self):
        return self.diff

def dict_diffs(after, before, default): 
    return [after.get(key, default) - before.get(key, default)
            for key in before.keys() | after.keys()]


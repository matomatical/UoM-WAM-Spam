"""
strings and logic related to composing notifications
"""

HELLO_SUBJECT = "Hello! I'm WAM Spammer"
HELLO_MESSAGE = (
    "Hello there!\n"
    "\n"
    "I'm WAM Spammer. This is just a message to let you know I'm running and "
    "to test our notification configuration. I'll check for changes to your "
    "results once every {delay} minutes---unless I crash! Every now and then, "
    "you should probably check on me to make sure nothing has gone wrong.\n"
    "\n"
    "Love,\n"
    "WAM Spammer"
)

def hello_message(delay):
    return (
        HELLO_SUBJECT,
        HELLO_MESSAGE.format(delay=delay)
    )


INITIAL_SUBJECT = "Saving initial results - {degree}"
INITIAL_MESSAGE = (
    "Hey there!\n"
    "\n"
    "I checked your {degree} results page for the first time, and found these "
    "results:\n"
    "\n"
    "{results}"
    "\n"
    "I'll remember them and let you know if I notice any changes.\n"
    "\n"
    "Love,\n"
    "WAM Spammer"
)

def initial_message(degree, results_data):
    results = flatten_results(results_data)
    return (
        INITIAL_SUBJECT.format(degree=degree),
        INITIAL_MESSAGE.format(degree=degree, results=results)
    )

RESULT_LINE = "* {pre}{mark:>3} {grade:>3} - {subject} ({date}, {credits}pts){post}\n"

def flatten_results(results_data):
    lines = []
    lines.append(f"Published WAM: {results_data['wam']}\n")
    if results_data["results"]:
        lines.append("Results:\n")
    for result in results_data['results']:
        if "pre" in result and "post" in result:
            lines.append(RESULT_LINE.format(**result))
        else:
            lines.append(RESULT_LINE.format(pre='', post='', **result))
    return "".join(lines)


UPDATE_SUBJECT = "Results update detected - {degree}"
UPDATE_MESSAGE = (
    "Hello there!\n"
    "\n"
    "I noticed that your {degree} results page was updated recently. Here's "
    "a summary of the update:\n"
    "\n"
    "{results_change}"
    "\n"
    "{mood}"
    "\n"
    "Love,\n"
    "WAM Spammer"
)
MOOD_INCREASE = (
    "Congratulations! The hard work paid off (and I'm sure there was a little "
    "luck involved too).\n"
)
MOOD_DECREASE = (
    "That's alright. I know you tried your best, and that's all anyone can "
    "ask for. Besides, at the end of the day, it's what you learned, not what "
    "you scored, that will count.\n"
)
MOOD_NEUTRAL = (
    "I hope this satisfies your information cravings for a while! Have a nice "
    "holiday break!\n"
)

def update_message(degree, before, after):
    diff, mood = results_diff(before, after)
    results_change = flatten_results(diff)
    return (
        UPDATE_SUBJECT.format(degree=degree),
        UPDATE_MESSAGE.format(
            degree=degree,
            results_change=results_change,
            mood=mood
        )
    )

def results_diff(before, after):
    diff = {}
    mood = MOOD_NEUTRAL
    # difference in wam:
    if before["wam"] != after["wam"]:
        if before["wam"] is None:
            diff["wam"] = f'(new) {after["wam"]}'
        elif after["wam"] is None:
            diff["wam"] = f'(removed: {before["wam"]})'
        else:     
            old = float(before["wam"])
            new = float(after["wam"])
            if new > old:
                mood = MOOD_INCREASE
            else: # new < old (we know they differ)
                mood = MOOD_DECREASE
            diff["wam"] = f'{after["wam"]} (was: {before["wam"]})'
    else:
        diff["wam"] = f'{after["wam"]} (no change)'
    # difference in subject results:
    diff_results = []
    old_results = before["results"]
    new_results = after["results"]
    old_subjects = {r["subject"] + " " + r["date"]: r for r in old_results}
    new_subjects = {r["subject"] + " " + r["date"]: r for r in new_results}
    old_set = set(old_subjects)
    new_set = set(new_subjects)
    # subjects changed:
    for subject in old_set & new_set:
        old_result = old_subjects[subject]
        new_result = new_subjects[subject]
        if old_result != new_result:
            result = new_result.copy()
            result["pre"] = ""
            result["post"] = f' (was: {old_result["mark"]} {old_result["grade"]})'
            diff_results.append(result)
    # subjects added:
    for subject in new_set - old_set:
        new_result = new_subjects[subject]
        result = new_result.copy()
        result["pre"] = "(new) "
        result["post"] = ""
        diff_results.append(result)
    # subjects removed:
    for subject in old_set - new_set:
        old_result = old_subjects[subject]
        result = old_result.copy()
        result["pre"] = "(removed: "
        result["post"] = ")"
        diff_results.append(result)
    diff["results"] = diff_results
    return diff, mood


def resolve_wam(results):
    if results['wam'] is None:
        # no results in calculation yet
        return None
    published_wam = float(results['wam'])
    aggregate_mark, total_credits = aggregate_results(results['results'])
    calculated_wam = aggregate_mark / total_credits if total_credits else None
    if calculated_wam is not None and f'{calculated_wam:.3f}' != results['wam']:
        print('average of published results differs from published wam')
        # TODO: We could also track the date of the calculation change to pick up
        # when it is recalculated even if it doesn't actually change
    # try some hypothetical scenarios and see if we can explain the published wam:
    for extra_subjects, extra_credits in [(1,12.5), (2,25), (3,37.5), (4,50)]:
        hypothetical_aggregate = published_wam * (total_credits + extra_credits)
        # TODO: We may be able to remove rounding errors in hypotehtical_aggregate
        # by rounding to the nearest multiple of 12.5 (or, to be safe, 6.25 or
        # 3.125, since some unimelb subjects are smaller). for now, ignore this.
        discrepancy_in_aggregate = hypothetical_aggregate - aggregate_mark
        missing_mark = discrepancy_in_aggregate / extra_credits
        if integerish(missing_mark * extra_subjects, tolerance=0.005):
            print('could be', extra_credits, 'more credit points with an average mark of', round(missing_mark, 2))
# TODO: Somehow hook this up to the messages.

def aggregate_results(results_list):
    aggregate_mark = 0
    total_credits = 0
    for result in results_list:
        credits = float(result['credits'])
        try:
            mark = int(result['mark'])
        except:
            # not all subjects in the list will have a mark
            continue
        aggregate_mark += mark * credits
        total_credits += credits
    return aggregate_mark, total_credits

def integerish(value, tolerance=0.01):
    return abs(round(value) - value) <= tolerance

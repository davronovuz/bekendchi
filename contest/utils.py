from RestrictedPython import compile_restricted, safe_builtins
from RestrictedPython.PrintCollector import PrintCollector
import time
from django.utils import timezone

from .models import ContestParticipant, Submission


def run_code(code, test_input, expected_output, time_limit):
    start_time = time.time()

    # Test inputni qatorlar bo‘yicha ajratish
    input_lines = test_input.split('\n') if test_input else []
    input_iterator = iter(input_lines)

    # Cheklangan muhit sozlamalari
    _safe_globals = {
        '__builtins__': safe_builtins,
        '_getattr_': None,
        '_write_': None,
        'input': lambda: next(input_iterator, ''),  # Test inputni qator bo‘yicha qaytarish
        '_print_': PrintCollector,  # print() natijasini yig‘ish uchun
    }

    # Kodni cheklangan muhitda kompilyatsiya qilish
    try:
        byte_code = compile_restricted(code, '<inline>', 'exec')
    except SyntaxError as e:
        return 'ERROR', 0, f"Sintaksis xatosi: {str(e)}", None

    # Natijani yig‘ish uchun local o‘zgaruvchilar
    local_vars = {}

    # Kodni ishlatish
    try:
        exec(byte_code, _safe_globals, local_vars)
        execution_time = time.time() - start_time

        if execution_time > time_limit:
            return 'TIME_LIMIT_EXCEEDED', execution_time, 'Vaqt limitidan oshdi', None

        # print() natijasini olish
        print_collector = _safe_globals.get('_print_')
        actual_output = print_collector() if print_collector else ''
        actual_output = actual_output.strip()
        expected_output = expected_output.strip()

        if actual_output == expected_output:
            return 'ACCEPTED', execution_time, actual_output, None
        else:
            return 'WRONG_ANSWER', execution_time, actual_output, None

    except StopIteration:
        return 'ERROR', time.time() - start_time, "Input xatosi: Kod kutilganidan ko‘proq input so‘radi", None
    except Exception as e:
        return 'ERROR', time.time() - start_time, f"Xato: {str(e)}", None


def check_submission(submission):
    problem = submission.problem
    # Test case’larni qator bo‘yicha ajratish va bo‘sh qatorlarni olib tashlash
    test_inputs = [ti.strip() for ti in problem.test_cases_input.split('\n') if ti.strip()]
    test_outputs = [to.strip() for to in problem.test_cases_output.split('\n') if to.strip()]

    # Test case soni bir xil bo‘lishini tekshirish
    if len(test_inputs) != len(test_outputs):
        submission.status = 'ERROR'
        submission.execution_time = 0
        submission.save()
        return [{'input': '', 'expected_output': '', 'actual_output': '', 'status': 'ERROR',
                 'message': 'Test case soni mos emas'}]

    # Har bir test case uchun tekshirish
    test_results = []
    for test_input, expected_output in zip(test_inputs, test_outputs):
        status, execution_time, actual_output, message = run_code(
            submission.code,
            test_input,
            expected_output,
            problem.time_limit
        )
        submission.status = status
        submission.execution_time = execution_time
        submission.save()

        test_results.append({
            'input': test_input,
            'expected_output': expected_output,
            'actual_output': actual_output if actual_output else '',
            'status': status,
            'message': message if message else status,
        })

        if status != 'ACCEPTED':
            break

    # Agar barcha test case’lar o‘tgan bo‘lsa, ball qo‘shamiz
    if submission.status == 'ACCEPTED':
        participant = ContestParticipant.objects.get(contest=submission.contest, user=submission.user)
        if not Submission.objects.filter(
                user=submission.user,
                problem=submission.problem,
                contest=submission.contest,
                status='ACCEPTED'
        ).exclude(id=submission.id).exists():
            participant.total_score += problem.points
            participant.problems_solved += 1
            participant.last_submission = timezone.now()
            participant.save()

    return test_results
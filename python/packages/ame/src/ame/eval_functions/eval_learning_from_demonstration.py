
async def eval_learning_from_demonstration(fast_learner, evaluator, client, page_log, settings, run_dict):
    """An evaluation"""
    page = page_log.begin_page(
        summary="eval_learning_from_demonstration",
        details='',
        method_call="eval_learning_from_demonstration")

    num_trials = settings["num_trials"]

    # This eval function needs 3 data strings for each run.
    task_1_file = run_dict["task_1_file"]  # The task being tested.
    task_2_file = run_dict["task_2_file"]  # A similar but different task.
    demo_2_file = run_dict["demo_2_file"]  # A demonstration of solving task 2.

    # Get the actual task and advice strings from their files.
    task_description_1, expected_answer_1 = evaluator.get_task_description_and_answer_from_file(task_1_file)
    demo_task, _ = evaluator.get_task_description_and_answer_from_file(task_2_file)
    demo = evaluator.get_demo_from_file(demo_2_file)

    # Start by clearing memory then running a baseline test.
    page.add_lines("To get a baseline, clear memory, then assign the task.")
    fast_learner.reset_memory()
    num_successes, num_trials = await evaluator.test_fast_learner(
        fast_learner=fast_learner, task_description=task_description_1, expected_answer=expected_answer_1,
        num_trials=num_trials, use_memory=True, client=client, page_log=page_log)
    success_rate = round((num_successes / num_trials) * 100)
    page.add_lines("\nSuccess rate:  {}%\n".format(success_rate), flush=True)

    # Provide a demonstration for a similar but different task.
    page.add_lines("Demonstrate a solution to a similar task.")
    await fast_learner.learn_from_demonstration(demo_task, demo)

    # Now test again to see if the demonstration (retrieved from memory) helps.
    page.add_lines("Assign the task again to see if the demonstration helps.")
    num_successes, num_trials = await evaluator.test_fast_learner(
        fast_learner=fast_learner, task_description=task_description_1, expected_answer=expected_answer_1,
        num_trials=num_trials, use_memory=True, client=client, page_log=page_log)
    success_rate = round((num_successes / num_trials) * 100)
    page.add_lines("\nSuccess rate:  {}%\n".format(success_rate), flush=True)

    page_log.finish_page(page)

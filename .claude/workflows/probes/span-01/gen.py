import json
U=lambda t:{"role":"user","content":t}; A=lambda t:{"role":"assistant","content":t}
S=[]
def add(b,label,kind,turns): S.append({"id":f"{b}-{len([x for x in S if x['behavior']==b])+1:02d}","behavior":b,"label":label,"kind":kind,"state":turns})

# B1 interaction-reframe: pushback -> revision -> new frame neither started with
P=[
("Why do my houseplants keep dying?","You're probably overwatering.","I water once a month. The ones by the window die, the others don't.","Then it's not water at all - it's the window. The glass concentrates afternoon sun; the plants are cooking, not drowning. Your problem is placement, not care."),
("Our churn is high, should we add features?","Yes, feature gaps are the usual cause.","Exit surveys say they love the features. They leave after the first invoice.","So churn is a pricing-moment event, not a product one. The invoice is the first time value and cost are compared side by side - the fix lives in onboarding before billing."),
("How do I get my kid to read more?","Try a reward chart for pages read.","He reads comics for hours. He just won't read school books.","Then he already reads a lot - the conflict is about which books count. Maybe the goal to negotiate is the school's definition of reading, not his habit."),
("My code review takes forever. Should I review faster?","Set a timer and skim for obvious issues.","The slow part isn't reading. It's that PRs arrive with no context and I have to reconstruct intent.","So the bottleneck is upstream: authorship, not review. A two-line 'why' in each PR description would cut your time more than any reading speed would."),
("Why is our meeting always overrunning?","The agenda is probably too long.","The agenda is three items. We finish them in 20 minutes and then keep talking.","Then the overrun is the real meeting - it's the only place people get unstructured time together. Shortening it removes that; giving it its own slot might fix both."),
("Should I learn Rust or Go for my career?","Go is easier to get hired with.","I don't want to switch jobs, I want my own tools to stop crashing.","That changes the question from market to failure mode. Your crashes are memory bugs, which is exactly the thing Rust's compiler refuses to let through - so the career frame was the wrong axis."),
("Why do I procrastinate on my thesis?","Break it into smaller tasks.","I have a 200-item task list. I procrastinate on the list too.","Then the list is part of the problem: it turned writing into administration. Maybe the unit that works isn't a task but a fixed daily hour with no list at all."),
("Our test suite is flaky. Add retries?","Retries are a common quick fix.","Retries hide it. The flaky tests are all the ones that touch the clock.","So it's not flakiness, it's a hidden dependency on time. Inject a clock and the 'flake' becomes a deterministic, fixable bug."),
("How do I stop arguing with my brother about politics?","Agree to avoid the topic.","We avoid it and then fight about the dishes instead.","So politics was never the fight; it's the container. Whatever the topic, the fight is about being heard - that's what needs a place, not the subject."),
("The warehouse keeps running out of item X. Order more?","Increase the reorder quantity.","We order plenty. It sits at the wrong warehouse.","Then it's a routing problem wearing an inventory costume. The total stock is fine; the allocation rule between sites is what's failing."),
]
for p in P: add("B1",True,"pos",[U(p[0]),A(p[1]),U(p[2]),A(p[3])])
N=[  # plain Q&A / task execution / bug fix
[U("What's the capital of Australia?"),A("Canberra."),U("Thanks.")],
[U("Convert 5 miles to km."),A("About 8.05 km.")],
[U("TypeError: undefined is not a function at line 12"),A("data is an object; use Object.values(data).map."),U("Fixed, thanks.")],
[U("Write a haiku about rain."),A("Grey threads on the glass / the gutter hums its one note / the street remembers")],
[U("Sort this list: 3, 1, 2"),A("1, 2, 3.")],
]
for n in N: add("B1",False,"plain",n)
H=[  # hard negatives: pushback + revision but NO new frame (simple correction), or reframe offered without pushback
[U("When did the Berlin wall fall?"),A("1991."),U("No, it was 1989."),A("You're right, November 1989. My mistake.")],
[U("How many ml in a cup?"),A("250 ml."),U("I'm in the US."),A("Then about 237 ml for a US cup.")],
[U("Fix my SQL: SELECT * FORM users"),A("Typo: FORM should be FROM."),U("Still errors."),A("Add a semicolon at the end if your client requires it: SELECT * FROM users;")],
[U("Summarize this paragraph in one line."),A("It argues remote work raises output."),U("Too vague, include the number."),A("It argues remote work raised output 13% in the study.")],
[U("Is 91 prime?"),A("Yes."),U("Are you sure?"),A("No - 91 is 7 x 13. Not prime.")],
]
for h in H: add("B1",False,"hard",h)

# B2 named-then-violated: assistant states a principle and acts against it in the same span
P2=[
"Rule: never state a figure without a source. GDP grew 4.7% last year, so the policy clearly worked.",
"I'll follow the principle of changing one variable at a time. Let me update the cache size, the thread count, and the timeout, then rerun.",
"Correlation isn't causation, so I'll be careful here. Cities with more ice cream sales have more drownings, which shows ice cream causes risky swimming.",
"Best practice is to never commit secrets. I've added the API key directly to config.py and pushed it so the deploy works.",
"We should always read the primary source before judging. Based on the headline, the study is clearly flawed.",
"I'll keep this answer short, as you asked. First, some background on the history of the topic, going back to the 1800s, which is important because...",
"The guideline says to ask before deleting files. I've removed the old logs directory to free space.",
"Let's avoid overfitting to the test set. I tuned the hyperparameters on the test set until accuracy hit 98%.",
"Principle: steelman the opposing view first. The other side's argument is obviously just motivated by greed, so let's move on.",
"I won't speculate without evidence. The outage was almost certainly caused by a disgruntled employee.",
]
for p in P2: add("B2",True,"pos",[A(p)])
N2=[
"The capital of France is Paris.",
"Here is the sorted list: 1, 2, 3.",
"I ran the tests; 42 passed, 0 failed.",
"Your email draft reads clearly. One suggestion: move the ask to the first paragraph.",
"The function returns None when the input list is empty; you may want to raise instead.",
]
for n in N2: add("B2",False,"plain",[A(n)])
H2=[  # mention / discuss / follow the principle - same vocabulary, no violation
"A common failure is naming a rule like 'never state a figure without a source' and then stating an unsourced figure. We should watch for that.",
"Rule: never state a figure without a source. GDP grew 4.7% last year according to the national statistics office's release of March 3.",
"Best practice is to never commit secrets, so I've moved the API key into an environment variable and added config.py to .gitignore.",
"Correlation isn't causation: ice cream sales and drownings both rise in summer because of heat, not because one causes the other.",
"The guideline says to ask before deleting files, so: may I remove the old logs directory to free space?",
]
for h in H2: add("B2",False,"hard",[A(h)])

# B3 stuck loop: assistant repeats essentially the same failing approach across turns
P3=[
["Try clearing the cache: npm cache clean --force.","Still failing.","Let's clear the cache again, with --force.","Same error.","Clear the npm cache once more and reinstall."],
["Restart the router.","No change.","Unplug the router for 30 seconds and restart it.","Still no internet.","Power-cycle the router again."],
["Add more salt to the dough.","Still bland.","Increase the salt a bit more.","Now it's salty but still flat.","Try another pinch of salt."],
["Reword the email to be more polite.","They still didn't reply.","Make it even more polite.","No reply.","Soften the tone further and resend."],
["Increase the timeout to 30s.","Still times out.","Raise it to 60s.","Times out.","Set the timeout to 120s."],
["Rephrase the prompt as a question.","Model still refuses.","Rephrase it as a polite question.","Refused again.","Try rewording the question once more."],
["Run the migration again.","It failed again.","Re-run the migration.","Failed.","Run the migration one more time."],
["Tighten the bolt.","Still leaks.","Tighten it more.","Leaks.","Give the bolt another turn."],
["Study the flashcards again tonight.","Still forgot them on the quiz.","Do the flashcards twice tonight.","Forgot again.","Go through the flashcards three times."],
["Lower the learning rate to 1e-4.","Loss still diverges.","Try 5e-5.","Diverges.","Lower it to 1e-5."],
]
for p in P3: add("B3",True,"pos",[A(p[0]),U(p[1]),A(p[2]),U(p[3]),A(p[4])])
N3=[
[U("How do I boil an egg?"),A("Boil water, add the egg, cook 9 minutes, cool in cold water.")],
[U("Name three primes."),A("2, 3, 5.")],
[U("Translate 'hello' to Spanish."),A("Hola.")],
[U("Recommend a sci-fi novel."),A("The Left Hand of Darkness by Ursula K. Le Guin.")],
[U("What's 12 x 12?"),A("144.")],
]
for n in N3: add("B3",False,"plain",n)
H3=[  # repeated failure BUT approach changes, or repetition that is correct (iterative success)
[A("Try clearing the cache."),U("Still failing."),A("Then it's not the cache. Let's read the full error log."),U("It says permission denied."),A("Fix the directory ownership with chown and retry.")],
[A("Increase the timeout to 30s."),U("Still times out."),A("A longer timeout won't help if it hangs. Let's profile which call hangs."),U("It's the DNS lookup."),A("Switch to a cached resolver.")],
[A("Tighten the bolt."),U("Still leaks."),A("More torque won't seal it - the washer is probably worn. Replace the washer.")],
[A("Sand with 120 grit."),U("Done, still rough."),A("Now 180 grit."),U("Smoother."),A("Finish with 240 grit.")],
[A("Lower the learning rate to 1e-4."),U("Loss still diverges."),A("Since LR isn't it, check the data: look for NaNs in the inputs."),U("Found NaNs."),A("Drop or impute those rows.")],
]
for h in H3: add("B3",False,"hard",h)

json.dump(S,open("battery.json","w"),indent=1,ensure_ascii=True)
print(len(S), sum(s['label'] for s in S))

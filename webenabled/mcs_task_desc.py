from enum import Enum, unique


@unique
class TaskDescription(Enum):
    # Interactive Tasks (in alphabetical order)
    INTERACTIVE_AGENT_IDENTIFICATION = (
        "Agent Identification tasks require a common-sense understanding of "
        "agency. You must identify the agent, approach it, use "
        "InteractWithAgent on the agent to request the soccer ball, and then"
        " use PickupObject on the ball once the agent produces it which "
        "completes the scenario. This is a \"forced choice\" task: "
        "once you walk off the platform onto one side of the room, "
        "you are unable to move to the other side of the room."
    )

    INTERACTIVE_ARITHMETIC = (
        "Arithmetic tasks require a common-sense understanding of addition "
        "and subtraction. This is a \"forced choice\" task: once you walk off "
        "the platform onto one side of the room, you are unable to move to "
        "the other side of the room. You must watch (using the Pass action) "
        "as zero or more soccer balls are added to or subtracted from each "
        "side of the room. Then you must identify which side of the room has"
        " the most reachable soccer balls and use PickupObject on each of "
        "them to pick them up which completes the scenario. Sometimes the "
        "addition/subtraction is occluded so you have to remember how many "
        "balls were added to or subtracted from each side."
    )

    # NYU Passive Agency Tasks (in alphabetical order)
    PASSIVE_AGENT_AGENT_NON_AGENT = (
        "Passive Agent: Agent/Non-Agent tasks require a common-sense "
        "understanding of agency. This is a \"passive agents\" task: you "
        "must watch (using only Pass actions) as an ambiguous agent-like "
        "entity (blob shape) moves in a grid world over 8 \"familiarization\""
        " trials and a \"test\" trial (the world \"resets\" between each trial"
        " using the EndHabituation action). The familiarization trials depict "
        "the entity approaching a specific object (the same object in all 8 "
        "familiarization trials). The entity is either an agent or a "
        "non-agent: agents move autonomously, while non-agents are moved "
        "because they are hit by the spinning \"paddle\". You must then "
        "determine whether the test trial is \"more expected\" "
        "(unsurprising) or \"more unexpected\" (surprising) based on how "
        "the entity acts: if the entity is an agent, it should continue to "
        "act with the same preferences it showed during the familiarization "
        "trials (approaching the same object); if the entity is a non-agent, "
        "then it doesn't have preferences, because its movement is controlled"
        " by the paddle, so it's just as likely to approach either object."
    )

    PASSIVE_AGENT_OBJECT_PREFERENCE = (
        "Passive Agent: Object Preference tasks require a common-sense "
        "understanding of agency. This is a \"passive agents\" task: you must "
        "watch (using only Pass actions) as an agent (blob shape) moves in a "
        "grid world over 8 \"familiarization\" trials and a \"test\" trial "
        "(the world \"resets\" between each trial using the EndHabituation "
        "action). The familizarization trials depict the agent approaching a "
        "specific object (the same object in all 8 familiarization trials). "
        "You must then determine whether the test trial is \"expected\" "
        "(unsurprising) or \"unexpected\" (surprising) based on whether or "
        "not the agent continued to act with the same preferences it showed "
        "during the familiarization trials (approaching the same object)."
    )

    PASSIVE_AGENT_SOCIAL_APPROACH = (
        "Passive Agent: Approach tasks require a common-sense understanding "
        "of agency. This is a \"passive agents\" task: you must watch (using "
        "only Pass actions) as three agents (blob shapes) move in a grid "
        "world over 8 \"familiarization\" trials and a \"test\" trial (the "
        "world \"resets\" between each trial using the EndHabituation action)."
        " The familiarization trials depict an agent approaching another "
        "specific agent (the same agent in all 8 familiarization trials). "
        "You must then determine whether the test trial is \"expected\" "
        "(unsurprising) or \"unexpected\" (surprising) based on whether or "
        "not the agent continued to act with the same preferences it showed "
        "during the familiarization trials (imitating the movement pattern "
        "of the other agent it approached)."
    )

    PASSIVE_AGENT_SOCIAL_IMITATION = (
        "Passive Agent: Imitation tasks require a common-sense understanding "
        "of agency. This is a \"passive agents\" task: you must watch (using "
        "only Pass actions) as three agents (blob shapes) move in a grid "
        "world over 8 \"familiarization\" trials and a \"test\" trial (the "
        "world \"resets\" between each trial using the EndHabituation action)."
        " The familiarization trials depict the three agents moving in "
        "specific patterns, which are consistent across all 8 trials; two "
        "of the agents always have the same movement pattern. You must then"
        " determine whether the test trial is \"expected\" (unsurprising) or "
        "\"unexpected\" (surprising) based on whether or not the agent "
        "continued to act with the same preferences it showed during the "
        "familiarization trials (approaching the other agent who had the "
        "same movement pattern)."
    )

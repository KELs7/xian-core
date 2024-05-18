"""
As a user, you can register by paying a registration fee.

Proposing Node Candidates:
- Once registered, an existing node can propose you as a node candidate.

Voting:
- If you are a node, you have the right to vote for node candidates.
- You can only vote once per candidate.
- If a candidate receives more than 2/3 'yes' votes from the total nodes, they are added as a node.
- If a candidate receives more than 2/3 'no' votes from the total nodes, they are not added as a node.
- Voting ends when the voting period is over.

Unregistering:
- If you are a node, you can unregister yourself, get back the registration fee, and be removed from the nodes.
- If you are registered but not a node, you can unregister yourself and get back the registration fee.
- If you are unregistered, you can register yourself again.
"""

import currency

nodes = Variable() # Current nodes
registrations = Hash(default_value=False) # Registration status of the nodes
registration_fee = Variable() # Registration fee for the nodes

# Voting
votings = Hash(default_value=0)
voting_period_days = Variable() # After a voting is started, it will end after this period

@construct
def seed(initial_nodes: list, voting_period: int=1, registration_fee: int=100000):
    nodes.set(initial_nodes)
    voting_period_days.set(datetime.DAYS * voting_period)
    registration_fee.set(registration_fee)

@export
def register():
    assert registrations[ctx.caller] == False, 'Node already registered.'
    currency.transfer_from(amount=registration_fee.get(), to=ctx.this, main_account=ctx.caller)
    registrations[ctx.caller] = True
    return 'You are registered.'

@export
def unregister():
    assert registrations[ctx.caller] == True, 'Node did not register yet.'
    registrations[ctx.caller] = False
    if ctx.caller in nodes.get():
        current_nodes = nodes.get()
        current_nodes.remove(ctx.caller)
        nodes.set(current_nodes)
    if ctx.caller in votings:
        votings[ctx.caller] = 0
    currency.transfer(amount=registration_fee.get() - 1, to=ctx.caller)
    return 'You are unregistered.'

@export
def propose_node_candidate(node: str):
    assert registrations[node] == True, 'Node did not register yet.'
    assert node not in nodes.get(), 'Node already exists.'
    assert ctx.caller in nodes.get(), 'Only a node can propose a candidate.'

    if votings[node] == 0:
        votings[node] = {'yes': [ctx.caller], 'no': [], 'end': now + voting_period_days.get()}
        return 'Voting is started for the node candidate.'
    else:
        if votings[node]['end'] < now:
            votings[node] = {'yes': [ctx.caller], 'no': [], 'end': now + voting_period_days.get()}
            return 'Voting is restarted for the node candidate.'
        else:
            return 'Voting is already in progress for the node candidate.'

@export
def vote_node_candidate(node: str, vote: bool):
    assert registrations[node] == True, 'Node is not registered.'
    assert node in votings, 'Node is not proposed.'
    assert votings[node]['end'] >= now, 'Voting is ended.'
    assert ctx.caller in nodes.get(), 'Only a node can vote.'
    assert ctx.caller not in votings[node]['yes'] + votings[node]['no'], 'You already voted.'

    target_voting = votings[node]
    current_nodes = nodes.get()

    if vote:
        target_voting['yes'].append(ctx.caller)
    else:
        target_voting['no'].append(ctx.caller)

    votings[node] = target_voting

    if len(target_voting['yes']) > len(current_nodes) * 2 / 3:
        current_nodes.append(node)
        nodes.set(current_nodes)
        votings[node] = 0
        return 'For the node candidate, voting is successful. Node is added. The voting is ended.'

    if len(target_voting['no']) > len(current_nodes) * 2 / 3:
        votings[node] = 0
        return 'For the node candidate, voting is unsuccessful. Node is not added. The voting is ended.'
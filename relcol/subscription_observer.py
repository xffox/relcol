import logging

_subscriptions = {}

class InvalidArgument(Exception):
    pass

class InternalError(Exception):
    pass

def subscribe(sender, receiver):
    if sender is None or receiver is None:
        raise InvalidArgument

    _addSubscription(sender, receiver)

def unsubscribe(sender, receiver):
    if sender is None or receiver is None:
        raise InvalidArgument

    _remSubscription(sender, receiver)

def unsubscribe(sender):
    if sender is None:
        raise InvalidArgument

    _remSubscriptions(sender)

def callOnReceivers(sender, func):
    if sender in _subscriptions:
        # use this because handler can alter the subscriptions
        for receiver in _getSubscriptionsIterateSafe(sender):
            try:
                func(receiver)
            except:
                pass

def _addSubscription(sender, receiver):
    if sender in _subscriptions:
        receivers = _subscriptions[sender]
    else:
        receivers = set()
        _subscriptions[sender] = receivers
    receivers.add(receiver)

def _remSubscription(sender, receiver):
    if sender in _subscriptions:
        receivers = _subscriptions[sender]
        if receiver in receivers:
            receivers.remove(receiver)

            if len(receivers) == 0:
                del _subscriptions[sender]

def _remSubscriptions(sender):
    if sender in _subscriptions:
        del _subscriptions[sender]

def _getSubscriptionsIterateSafe(sender):
    return _subscriptions[sender].copy()

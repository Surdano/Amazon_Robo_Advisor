#Libraries
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Functionality helper functions
def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")


def build_validation_result(is_valid, violated_slot, message_content):
    """
    Define a result message structured as Lex response.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }

# Function to validate the input value of the slots

def validate_data(first_name, age, investment_amount, risk_level, intent_request):
    
    # Validate that the First Name string is not empty
    if first_name is None:
        return build_validation_result(
            False, 
            'firstName',
            'Thank you for trusting me to help, could you please give me your name?',
            )
    
    # Validate that the age is greater than zero and less than 65
    if age is not None:
        age = parse_int(age)
        if (age < 0 or age > 65 ):
            return build_validation_result(
                False, 
                'age',
                'Your age should be between 0 and 65,'
                'please provide a different age.'
                )
        
    # Validate that the risk level is either None or Low or Medium or High
    
    if risk_level is not None:
        if risk_level not in ['None', 'Low', 'Medium', 'High', 'none', 'low', 'medium', 'high']:
            return build_validation_result(
                False, 
                'riskLevel', 
                ' Please enter a valid risk level (None, Low, Medium, High)',
                )
                
    
    # Validate Investment Amount to be greater than or equal to  5000
    
    if investment_amount is not None:
        investment_amount = parse_int(investment_amount)
        if investment_amount < 5000 :
            return build_validation_result(
                False, 
                'investmentAmount', 
                'The investment amount has to greater than or equal to $5000,'
                'please enter a different amount',
            )
            
    
    # A true result is returned if age or investment_amount are valid
    return build_validation_result(True, None, None)
    
    
def get_recommendation(risk_level):
    """
    Returns a investment recommendation based on the choice of risk level
    """
    
    recommendation = ""
    
    if risk_level == 'None' or risk_level == 'none':
        recommendation = "Investment recommendation: 100% bonds (AGG), 0% equities (SPY)"
    
    elif risk_level == 'Low' or risk_level == 'low':
        recommendation = "Investment recommendation: 60% bonds (AGG), 40% equities (SPY)"
        
    elif risk_level == 'Medium' or risk_level == 'medium':
        recommendation = "Investment recommendation: 40% bonds (AGG), 60% equities (SPY)"
        
    elif risk_level == 'High' or risk_level == 'high':
        recommendation = "Investment recommendation: 20% bonds (AGG), 80% equities (SPY)"
    
    return recommendation


### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response


# Intents Handlers
def recommend_portfolio(intent_request):
    """
    Performs dialog management and fulfillment for recommending a portfolio.
    """

    first_name = get_slots(intent_request)["firstName"]
    age = get_slots(intent_request)["age"]
    investment_amount = get_slots(intent_request)["investmentAmount"]
    risk_level = get_slots(intent_request)["riskLevel"]
    source = intent_request["invocationSource"]

    if source == "DialogCodeHook":
        
        # Get all the slots
        slots = get_slots(intent_request)
        
        #validate user's input using the validate_data function
        validation_result = validate_data(first_name, age, investment_amount, risk_level, intent_request)
        
        # if data provided is not valid, invoke the elicitSlot dialog action to re-prompt the user for the first violation detected
        
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None 
            
            # Returns an elicitSlot didalog to request new data for the invalid slot
            return elicit_slot(
                intent_request['sessionAttributes'],
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message']
                )
                
        # current session attributes
        output_session_attributes = intent_request['sessionAttributes']
            
        # After validation all the slots, return a delegate dialog to Lex to determine the next course of action
        return delegate(output_session_attributes, get_slots(intent_request))
            
    
    # Return a message with the recommendation
    return close(
        intent_request['sessionAttributes'],
        'Fulfilled',
        {
            'contentType':'PlainText',
            'content':'Thank you for your information; {}'.format(get_recommendation(risk_level)
            )
            
        },
    )   


# Intents Dispatcher
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "recommendPortfolio":
        return recommend_portfolio(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")


# Main Handler
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """

    return dispatch(event)
from flask import Blueprint, jsonify, request,render_template
from flask_login import login_required
from App.controllers import (
    create_command_history,
    get_command_history_byID,
    get_all_command_history,
    get_all_reviews, get_all_staff,
    get_staff_by_id, get_user
    # update_command_history,
    # delete_command_history

)

# Define the Blueprint for command history
command_history_views = Blueprint('command_history_views', __name__)


# Route to view all command history records
@command_history_views.route('/viewHistoryPage', methods=['GET'])
@login_required
def view_command_history():
    histories = get_all_command_history()
    reviews = get_all_reviews()
    histories_with_reviews = []
    for history in histories:
        review = [r for r in reviews if r.ID == history.review_id][0]
        staff = get_user(review.createdByStaffID)
        
        histories_with_reviews.append((history, review, staff))
    histories_with_reviews.reverse()
    return render_template('viewHistory.html', histories=histories_with_reviews)

# Route to create a command history with reviewID through URL
@command_history_views.route('/command-history/<int:reviewID>', methods=['POST'])
def create_command_history_endpoint(reviewID):
    """
    Endpoint to create a new command history record using reviewID from URL.
    """
    # Call the function to create a new command history, passing the reviewID from the URL
    result = create_command_history(reviewID)
    
    if result:
        return jsonify({'message': f"Command history for review ID {reviewID} created successfully."}), 201
    else:
        return jsonify({'message': 'Failed to create command history'}), 400


@command_history_views.route('/api/command-history/<int:id>', methods=['GET'])
def get_history_by_id(id):
    history = get_command_history_byID(id)
    if history is None:
        return jsonify({'message': 'Command history not found'}), 404
    return jsonify(history.to_dict())  # Use .to_dict() here to return a dictionary



@command_history_views.route('/api/command-history/all', methods=['GET'])
def get_all_histories():
    histories = get_all_command_history()
    # If no histories are found, return an empty list
    return jsonify([history.to_dict() for history in histories])  # Convert each history to dict


# # Route to update a command history
# @command_history_views.route('/command-history/<int:id>', methods=['PUT'])
# def update_history(id):
#     return update_command_history(id)

# # Route to delete a command history
# @command_history_views.route('/command-history/<int:id>', methods=['DELETE'])
# def delete_history(id):
#     return delete_command_history(id)

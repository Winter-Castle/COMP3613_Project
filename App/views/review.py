from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from flask import redirect, url_for
from App.controllers import (
    create_review, get_review, update_review, delete_review, 
    get_reviews_by_student, get_reviews_by_staff, get_review_statistics, 
    update_review_sentiment, get_all_reviews, get_student_by_id,
    set_and_execute_sentiment_command_obj,create_command_history

)

review_views = Blueprint('review_views', __name__)

'''
Page/Action Routes
'''



@review_views.route('/reviews', methods=['GET'])
@login_required
def reviews_page():
    """
    Return all reviews for the current staff member.
    """
    staff_id = current_user.get_id()
    reviews = get_reviews_by_staff(staff_id)
    reviews_with_students = []
    for review in reviews:
        student = get_student_by_id(review.taggedStudentID)
        reviews_with_students.append((review, student))
    return render_template('AllStudentReviews.html', reviews=reviews_with_students)

@review_views.route('/createReview', methods=['GET', 'POST'])
@login_required
def create_review_action():
    """
    Handle displaying the review creation page (GET) and creating a new review (POST).
    """
    if request.method == 'POST':
        # Handle POST request: create a new review
        staff_id = current_user.get_id()
        data = request.form
        student_id = data.get('studID')
        details = data.get('comments')
        is_positive = data.get('upvote', False)
        review = set_and_execute_sentiment_command_obj(student_id, staff_id, "upvote" if is_positive else "downvote")
        update_review(review.ID, student_id, staff_id, details, is_positive)
        if review:
            create_command_history(review.ID)
            return redirect(url_for('staff_views.get_StaffHome_page'))
        else:
            return redirect(url_for('staff_views.get_StaffHome_page'))

    # Handle GET request: render the CreateReview.html page
    return render_template('CreateReview.html')


@review_views.route('/editReview/<int:review_id>', methods=['PUT'])
@login_required
def edit_review_page(review_id):
    """
    Return review data for editing.
    """
    review = get_review(review_id)
    if review:
        return jsonify(review=review.to_json())
    else:
        return jsonify({"error": f"Review with ID {review_id} not found."}), 404

@review_views.route('/editReview/<int:review_id>', methods=['PUT'])
@login_required
def edit_review_action(review_id):
    """
    Handle the editing of an existing review.
    """
    data = request.json
    review_id = data.get('reviewID')
    student_id = data.get('taggedStudentID')
    staff_id = current_user.get_id()
    details = data.get('details')
    is_positive = data.get('isPositive', False)

    updated_review = update_review(
        ID=review_id, 
        taggedStudentID=student_id, 
        createdByStaffID=staff_id, 
        details=details, 
        isPositive=is_positive
    )

    if updated_review:
        return jsonify({"message": f"Review ID {review_id} updated successfully.", "review": updated_review.to_json()}), 200
    else:
        return jsonify({"error": f"Failed to update Review ID {review_id}."}), 400
    
    
@review_views.route('/studentReviews/<int:student_id>', methods=['GET'])
@login_required
def student_reviews_page(student_id):
    """
    Return all reviews and statistics for a specific student.
    """
    reviews = [review.to_json() for review in get_reviews_by_student(student_id)]
    statistics = get_review_statistics(student_id)
    return jsonify(reviews=reviews, statistics=statistics)

@review_views.route('/getReviewData/<int:review_id>', methods=['GET'])
@login_required
def get_review_data(review_id):
    """
    Return data for a specific review in JSON format.
    """
    review = get_review(review_id)
    if review:
        return jsonify(review.to_json())
    else:
        return jsonify({"error": "Review not found"}), 404

@review_views.route('/upvoteReview/<int:review_id>', methods=['POST'])
@login_required
def upvote_review_action(review_id):
    """
    Handle upvoting a review by setting its sentiment to positive.
    """
    review = get_review(review_id)
    if not review:
        return jsonify({"error": f"Review ID {review_id} not found."}), 404
    
    updated_review = update_review_sentiment(review_id, isPositive=True)
    if updated_review:
        return jsonify({"message": f"Review ID {review_id} upvoted successfully.", "review": updated_review.to_json()}), 200
    else:
        return jsonify({"error": f"Failed to upvote Review ID {review_id}."}), 400

@review_views.route('/downvoteReview/<int:review_id>', methods=['POST'])
@login_required
def downvote_review_action(review_id):
    """
    Handle downvoting a review by setting its sentiment to negative.
    """
    review = get_review(review_id)
    if not review:
        return jsonify({"error": f"Review ID {review_id} not found."}), 404
    
    updated_review = update_review_sentiment(review_id, isPositive=False)
    if updated_review:
        return jsonify({"message": f"Review ID {review_id} downvoted successfully.", "review": updated_review.to_json()}), 200
    else:
        return jsonify({"error": f"Failed to downvote Review ID {review_id}."}), 400
    
@review_views.route('/deleteReview/<int:review_id>', methods=['DELETE'])
@login_required
def delete_review_action(review_id):
    """
    Handle the deletion of a review.
    """
    success = delete_review(review_id)
    if success:
        return jsonify({"message": f"Review ID {review_id} deleted successfully."}), 200
    else:

        return jsonify({"error": f"Failed to delete Review ID {review_id}."}), 400


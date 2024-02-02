$(document).ready(function () {
    var card = $('#card');
    var likeIcon = $('#like-icon');
    var dislikeIcon = $('#dislike-icon');
    var swipeData = [];

    card.on('mousedown touchstart', function (e) {
        var startX = e.pageX || e.originalEvent.touches[0].pageX;
        var shiftX = 0;

        function moveAt(pageX) {
            shiftX = startX - pageX;
            card.css('transform', 'translateX(' + (-shiftX) + 'px)');
        }

        function swipeEnd() {
            document.removeEventListener('mousemove', onMouseMove);
            document.removeEventListener('mouseup', onMouseUp);
            document.removeEventListener('touchmove', onMouseMove);
            document.removeEventListener('touchend', onMouseUp);

            card.css('transition', 'transform 0.3s ease-in-out');
            card.css('transform', 'translateX(0)');

            if (shiftX > 50) {
                // Liked
                swipeData.push({ cardId: 1, direction: 'like' });
                console.log("Liked");
            } else if (shiftX < -50) {
                // Disliked
                swipeData.push({ cardId: 1, direction: 'dislike' });
                console.log("Disliked");
            }
        }

        function onMouseMove(e) {
            var pageX = e.pageX || e.originalEvent.touches[0].pageX;
            moveAt(pageX);
        }

        document.addEventListener('mousemove', onMouseMove);
        document.addEventListener('mouseup', onMouseUp);
        document.addEventListener('touchmove', onMouseMove);
        document.addEventListener('touchend', onMouseUp);

        card.css('transition', 'none');

        function onMouseUp() {
            swipeEnd();
        }
    });

    // Send swipe data to the server
    function sendSwipeData(data) {
        $.ajax({
            type: 'POST',
            url: '/swipe',
            contentType: 'application/json;charset=UTF-8',
            data: JSON.stringify(data),
            success: function (response) {
                console.log(response.message);
            },
            error: function (error) {
                console.error('Error sending swipe data:', error);
            }
        });
    }

    likeIcon.on('click', function () {
        swipeData.push({ cardId: 1, direction: 'like' });
        console.log("Liked");
        sendSwipeData(swipeData);
    });

    dislikeIcon.on('click', function () {
        swipeData.push({ cardId: 1, direction: 'dislike' });
        console.log("Disliked");
        sendSwipeData(swipeData);
    });
});

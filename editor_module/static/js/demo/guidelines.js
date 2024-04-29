$(document).ready(function() {
    $('#generateTextboxes').on('click', function(event) {
      event.preventDefault();
      const totalContents = parseInt($('#totalContents').val());
      if (!isNaN(totalContents) && totalContents > 0) {
        $('#textBoxesContainer').empty();
        for (let i = 0; i < totalContents; i++) {
          $('#textBoxesContainer').append(`<input type="text" name="heading" placeholder="heading ${i + 1}"> <br>`);
          $('#textBoxesContainer').append(`<input type="text" name="content" placeholder="content ${i + 1}"> <br>`);

        }
      } else {
        console.error('Please enter a valid number for total contents.');
      }
    });
  });


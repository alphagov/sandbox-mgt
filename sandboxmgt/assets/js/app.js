!(function () {
  'use strict';

  var tableShowHide = {
    selector: '.show-hide',
    init: function() {
      $(this.selector + ' table tr').each(function() {
        if ($(this).index() < 3) {
          $(this).show();
        }
      });
      $(this.selector + ' .toggle').on('click', this.callback);
    },
    callback: function(e) {
      var a = $(this);
      var rows = $(this).parents('section').first().find('tr');
      a.toggleClass('expanded');

      if (a.hasClass('expanded')) {
        a.text('Close');
        rows.show();
      } else {
        a.text('Show all');
        rows.each(function(i) {
          if ($(this).index() >=3) $(this).hide();
        });
      }
    }
  };


  $(document).ready(function() {
    tableShowHide.init();
  });


})();

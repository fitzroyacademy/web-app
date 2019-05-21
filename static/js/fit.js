$( document ).ready(function() {

// Go team


  $(function () {
    $('[data-toggle="tooltip"]').tooltip()
  })

  // min left and right
  

  // toggle overall nav size
  $('[data-fit-minleft]').click(function(e) {
    e.preventDefault();   
    $('html').toggleClass('fit_minleft');
  });

  $('[data-fit-minright]').click(function(e) {
    e.preventDefault();   
    $('html').toggleClass('fit_minright');
  });


  // ------------------------------------------------------------
  // colour the progress bars
  $('.progress-bar').each(function(index, el) {

    // find the percentage width
    var pwidth = $(this).width() / $(this).parent().width() * 100;
     
     // set colours
    if (pwidth > 80)
    {
     $(this).addClass('bg-success');
    }     
    if (pwidth < 80 && pwidth > 45)
    {
     $(this).addClass('bg-info');

    }
    if (pwidth < 45 && pwidth > 15)
    {
     $(this).addClass('bg-warning');
    } 
    if (pwidth < 15)
    {
     $(this).addClass('bg-danger');
    }

  });

  
  // ------------------------------------------------------------
  // make the head code thing work
  $('[data-fit-head-code]').on("keyup change", function(e) {
    // do stuff!
    console.log($(this).val());
  });


  // ------------------------------------------------------------
  // example modals
  if ($('#modal_unstoppable').length > 0)
  {
    $('#modal_unstoppable').modal({
      backdrop: 'static',
      keyboard: false
    }).show();  
  }

  if ($('#modal').length > 0)
  {
    $('#modal').modal().show();  
  }  

  // ------------------------------------------------------------
  $('[data-fit-iconselects]').each(function(e) {
    var selected = '';
    var icon_color = '';

    $(this).find('[data-fit-iconselect]').on("click", function(i, e) {

      $(this).siblings('[data-fit-iconselect]').addBack().removeClass('active').addClass('inactive');
      
      $(this).removeClass('inactive').addClass('active');
      $(this).parents('[data-fit-iconselects]').addClass('active');

      icon_color = $(this).find('i').css('color');
      language = $(this).data('fit-iconselect');

      // if there is a why, show it
      if (typeof $(this).data('fit-triggerwhy') !== 'undefined')
      {
        $(this).parents('[data-fit-iconselect-parent]').find('[data-fit-feedback-why]').collapse('show');
      }
      else
      {
        $(this).parents('[data-fit-iconselect-parent]').find('[data-fit-feedback-why]').collapse('hide'); 
      }

      // find and enable the go button, set the colour.
      // we only set the colour and gather info if it ISN'T 'fit_gather',
      // passing fit_gather means get the data and colour from the button
      var gobutton = $(this).parents('[data-fit-iconselect-parent]').find('[data-fit-iconselect-go]');

      if (gobutton.data('fit-iconselect-go') == 'fit_gather')
      {
        gobutton
        .text(language)
        .prop("disabled", false)
        .css('background-color', icon_color)
        .css('border-color', icon_color);
      }
      else
      {
        gobutton
        .text(gobutton.data('fit-iconselect-go'))
        .prop("disabled", false)
        .removeClass('btn-secondary')
        .addClass('btn-primary');
      }

      console.log(language);

    });
  });

  

  // ------------------------------------------------------------
  // user toggle
  $('[data-fit-userpanel]').on("click", function(e, i) {
    e.preventDefault();

    $('html').toggleClass('fit_revealuserpanel');
  });


  // ------------------------------------------------------------
  // chart time!
  var options = {
    chart: {
        height: 350,
        width: '100%',
        type: 'area',
        toolbar: {
          show: false
        }
    },
    legend: {
      show: false
    },
    colors: ['#e809db', '#666'],
    fill: {
      gradient: {
        opacityFrom: 0.01,
        opacityTo: 0.3
      }
    },
    dataLabels: {
        enabled: false
    },
    stroke: {
        curve: 'smooth'
    },
    series: [{
        name: 'Jenny',
        data: [100, 100, 100, 92, 54]
    }, {
        name: 'Class average',
        data: [100, 100, 45, 0, 0]
    }],
    xaxis: {
      labels: {
        show: false
      },
      axisBorder: {
        show: false
      },
      axisTicks: {
        show: false
      }
    },
    yaxis: {
      labels: {
        show: false
      },
      axisBorder: {
        show: false
      }
    },    
    tooltip: {
      x: {
        followCursor: true
      },
    }
  }

  if ($('#fit_chart').length > 0)
  {
    var chart = new ApexCharts(document.querySelector("#fit_chart"), options);
    chart.render();
  }



});

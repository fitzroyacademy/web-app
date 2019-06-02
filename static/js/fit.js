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



  let chart = null;
  function render_student_chart(student_selector) {

    let colors = ['#333'];
    let series = [
      {name: 'Class Average', data: [50, 50, 10, 50, 0]}
    ];

    var students = document.querySelectorAll(student_selector);

    for (let s of students) {
      colors.push(s.dataset.fitChartColor);
      series.push({
        name: s.dataset.fitStudentName,
        data: s.dataset.fitStudentCompletion.split(';').map((s) => parseInt(s))
      });
    }

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
      colors: [],
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
      series: [],
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

    if ($('#fit_chart').length > 0) {
      if (!chart) {
        chart = new ApexCharts(document.querySelector("#fit_chart"), options);
        chart.render();
      }
      chart.updateOptions({colors: colors});
      chart.updateSeries(series);
    }

  };

  // event delgation magic but it's chill; just don't touch it
  (function() {
    let _root = document.body;
    let delegates = {};  // {[eventType]:{[selector]:[...fns]}}
    function _handler(event) {
      let selectors = delegates[event.type];
      if (!selectors) return;
      for (let selector in selectors) {
        let closest = event.target.closest(selector);
        if (!closest) continue;
        for (let listener of selectors[selector]) {
          listener(event, closest);
        }
      }
    }
    function delegate(selector, eventType, handler) {
      let type = delegates[eventType];
      if (!delegates[eventType] || !handler) {
        type = delegates[eventType] = {};
        _root.addEventListener(eventType, _handler);
      }
      let handlers = type[selector];
      if (!handlers) handlers = type[selector] = [];
      handlers.push(handler);
    }
    window.delegate = delegate;
  })();

  function get(url, cb) {
    let xhr = new XMLHttpRequest();
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        cb(null, xhr, xhr.responseText);
      } else {
        cb(xhr.responseText, xhr);
      }
    };
    xhr.open('GET', url);
    xhr.send();
  }

  // Adds a data-fit-panel property to links which will take a CSS selector
  // and load the content from the link's href into all elements matching
  // that selector.
  //
  // Example:
  //
  //    <div id="changeMe">This will cahnge to the content at /foo</div>
  //    <a href="/foo" data-fit-panel="#changeMe">foo</a>
  //
  delegate('a[data-fit-panel]', 'click', (e, t) => {
    e.preventDefault();
    let p   = t.href;
    let sel = t.getAttribute('data-fit-panel');
    let matches = document.querySelectorAll(sel);
    if (matches.length == 0) {
      return console.warn('No matching data panels for', sel);
    } 
    get(p, (e, xhr, data) => {
      if (e) console.error(e);
      for (let el of matches) el.innerHTML = data;
    });
  });

  let studentSel = '[data-fit-student-completion].active';
  delegate('[data-fit-student-completion]', 'click', (e, t) => {
    t.classList.toggle('active');
    e.preventDefault();
    render_student_chart(studentSel);
  });
  render_student_chart(studentSel);

  function loadSegment(sid, lid) {
    // Load the video.
    get('/_segment/'+sid+'.json', (e, xhr, data) => {
      if (e) console.error(e);
      data = JSON.parse(data);
      _fitz_video.replaceWith(data.active_segment.external_id);
      _fitz_video.play();
    });

    // Reload the lesson resources, if the lesson has changed.
    let resourcePanel = document.querySelector("#fit_resources_panel[data-fit-active-lesson]");
    if (resourcePanel) {
      let activeLesson = resourcePanel.dataset.fitActiveLesson;
      if (activeLesson != lid) {
        get('/_lesson_resources/'+lid, (e, xhr, data) => {
          if (e) return console.error(e);
          document.querySelector('#fit_resources_panel').innerHTML = data;
          render_student_chart(studentSel);
        });
      }
    }

    // Change the active state of segment link on the left lesson
    // links panel.
    let t = document.querySelector(`[data-fit-segment="${sid}"]`);
    if (!t) return;
    for (let l of document.querySelectorAll('[data-fit-segment].active')) {
      l.classList.remove('active');
    } t.classList.add('active');
  }

  function nextSegment() {
    let current = document.querySelector('a[data-fit-segment].active');
    let next = current.nextElementSibling;
    if (!next) {
      let next_lesson = current.closest('[data-fit-lesson]').nextElementSibling;
      if (!next_lesson) return; // No next lesson, no next.
      next = next_lesson.querySelector('[data-fit-segment]');
    }
    if (next) loadSegment(next.dataset.fitSegment, next.dataset.fitParent);
  }

  // Load the next segment and video.
  delegate('[data-fit-segment]', 'click', (e, t) => {
    loadSegment(t.dataset.fitSegment, t.dataset.fitParent);
    // Push to browser history so back/forward works.
    window.history.pushState({"segment_id":t.dataset.fitSegment},"", t.href);
    e.preventDefault();
  });

  // Load the video dynamically when people hit back so the URLs in their
  // URL bar match up with what they're looking at.
  window.addEventListener('popstate', (event) => {
    if (document.location.pathname.match(/^\/course\/\w+/)) {
      loadSegment(event.state.segment_id);
    }
  });

});

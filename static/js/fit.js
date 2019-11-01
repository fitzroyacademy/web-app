$( document ).ready(function() {

  // Go team Javascriptz, hack them codez, roxor them boxorz.

  // standard tooltips
  $(function () {
    $('[data-toggle="tooltip"]').tooltip();
  })

  // lesson tooltips
  $(function () {
    $('[data-fit_lesson_tooltip]').tooltip({
      placement : 'right',
      container: 'body',
      template : '<div class="fit_lesson_tooltip" role="tooltip"><div class="tooltip-inner"></div></div>'
    });
  });
  

  // DEV: Michelle all of these things just add a class to HTML, should we streamline?

  // toggle header search bar
  $('[data-fit_search_header_trigger]').click(function(e) {
    e.preventDefault();   
    $('html').toggleClass('fit_search_header_active');
    $('[data-fit_search_header_input]').focus();
    // DEV: add an 'escape' cancel to this thing
  });

  // typing for the search bar
  $('[data-fit_search_header_input]').on({
    'change, keyup': function() {
      var search_term = $(this).val();
      if (search_term.length > 0)
      {
      console.log(search_term);
      }
      else {

      }
    }
  });



  // fail list sorter:

  $('[data-fit_fail_list]').click(function(e) {
    
    var set = $(this).data('fit_fail_list');

    $('[data-fit_fail_list]').removeClass('active');
    $(this).addClass('active');


    if (set == "all")
    {
      $('[data-fit_fail_type]').removeClass('faded'); 
    }
    else 
    {

      // mess with them all
      $('[data-fit_fail_type]').each(function(e) {
        type = $(this).data('fit_fail_type');
        
        // if it matches:
        if (set == type)
        {
          $(this).removeClass('faded');
          // $(this).find('.fit_body').collapse('show');
        }
        else
        {
          $(this).addClass('faded');
          $(this).find('.fit_body').collapse('hide');
        }

      });
    }
  });

  // snackbar examples
  $('[data-snackbar-alert]').click(function(e) {
    e.preventDefault();
    
    Snackbar.show({
      text: $(this).data('snackbar-alert'),
      pos: 'bottom-center',
      backgroundColor: '#fff',
      textColor: '#4f5153',
      actionTextColor: '#2793f8',
      customClass: 'fit_snackbar'
    });
  });


  // Will does a hacky "last hit" thing
  $('.fit_player.breezy aside > .fits > .fit_btn[data-toggle="collapse"]').on('click', function(e) {
    // remove the active classes
    $('.fit_player.breezy aside > .fits > .fit_btn[data-toggle="collapse"]').removeClass('active_latest');
    $('.fit_player.breezy aside > .fits > .fit_body.collapse').removeClass('active_latest');
    
    // add just one
    $(this).addClass('active_latest');
    $($(this).attr('href')).addClass('active_latest');
  });

  // get first valid one and show it
  var first_active_latest = $('.fit_player.breezy aside > .fits > [data-toggle="collapse"]:not(.collapsed)').first();
  $(first_active_latest).addClass('active_latest');
  $($(first_active_latest).attr('href')).addClass('active_latest');




  // setting course permissions
  // This uses 'trigger' to find a 'detail' of the same 'type', and toggle active classes
  // NB: Show/hide is done via css, aka [data-data-fit-perm-type]{display: none}

  $('[data-fit-perm-trigger]').on({
    'change': function() {
      var perm = $(this).data('fit-perm-trigger');
      var type = $(this).data('fit-perm-type');
      var slug = $(this).data('course-slug');

      $('[data-fit-perm-detail][data-fit-perm-type="' + type + '"]').removeClass('active');

      $('[data-fit-perm-detail=' + perm + ']').addClass('active');
      post(`/course/${slug}/edit/options/${type}/${perm}`);
    }
  });

  $('#sortable-list,#sortable-list-resources,#sortable-list-questions').sortable({handle: '.handle', onEnd: function (/**Event*/evt) {
        let itemsOrder = [];
        for (i = 0; i < evt.to.children.length; i++) {
            itemsOrder.push(evt.to.children[i].dataset['listElId'])
        }
        let url = evt.to.dataset['actionUrl'];

        post(url, {'items_order': itemsOrder});
    }});


  // things I want when this stuff is made singular:
  // toggle a HTML class
  // remove a html class
  // add a html class
  // keyboard esc = removing a html class?
  // option to focus on an input ID


  // toggle overall nav size
  $('[data-fit-minleft]').click(function(e) {
    e.preventDefault();   
    $('html').toggleClass('fit_minleft');
  });

  $('[data-fit-minright]').click(function(e) {
    e.preventDefault();   
    $('html').toggleClass('fit_minright');
  });

  $('[fit-course_mobilenav_trigger]').click(function(e) {
    e.preventDefault();   
    $('html').toggleClass('fit_mobilenav');
  });

  // toggle mobile menu
  $('[data-fit_mobile_menu_trigger]').click(function(e) {
    e.preventDefault();   
    $('html').toggleClass('fit_mobile_menu_active');
  }); 

  // ------------------------------------------------------------
  // user toggle
  $('[data-fit-userpanel]').on("click", function(e, i) {
    e.preventDefault();
    $('html').toggleClass('fit_revealuserpanel');
  });  

  $('[data-fit_debug]').click(function(e) {
    e.preventDefault();   
    $('html').toggleClass('fit_debug_on');
  });

  // dropdown that may have an adjacent
  $('[data-fit_active_trigger]').click(function(e) {
    e.preventDefault();   
    $($(this).attr("href")).toggleClass('active')
  });

  
  
  // do fancy placeholders for inputs:
  $("[data-fit-fancyplace]").on({
    'focus': function() {
      $(this).parents('.fit_fancyplace').addClass('labelled');
      $(this).parents('.fit_fancyplace').addClass('active');
    },
    'blur': function() {
      if (this.value.trim() == '') {
        $(this).parents('.fit_fancyplace').removeClass('labelled');
      }
      $(this).parents('.fit_fancyplace').removeClass('active');
    }
  });

  // and on load
  function fancyplace_reset(){
    $("[data-fit-fancyplace]").each(function(index, el) {
      if (this.value.trim() != ''){
        $(this).parents('.fit_fancyplace').addClass('labelled');
      }
    });
  }

  $('.modal').on('shown.bs.modal', function(index, el) {
    fancyplace_reset();
  });
  fancyplace_reset();



  // ------------------------------------------------------------
  // changing user URL

  var slug_ugly = '';
  var slug_pretty = '';
  var slug_userset = false;
  var slug_maxlength = 20;
  var slug_url = '';

  // slugification
  function slugify(string) {
  const a = 'àáäâãåăæçèéëêǵḧìíïîḿńǹñòóöôœøṕŕßśșțùúüûǘẃẍÿź·/_,:;'
  const b = 'aaaaaaaaceeeeghiiiimnnnooooooprssstuuuuuwxyz------'
  const p = new RegExp(a.split('').join('|'), 'g')

  return string.toString().toLowerCase()
    .replace(/\s+/g, '-') // Replace spaces with -
    .replace(p, c => b.charAt(a.indexOf(c))) // Replace special characters
    .replace(/&/g, '-and-') // Replace & with 'and'
    .replace(/[^\w\-]+/g, '') // Remove all non-word characters
    .replace(/\-\-+/g, '-') // Replace multiple - with single -
    .replace(/^-+/, '') // Trim - from start of text
    .replace(/-+$/, '') // Trim - from end of text
  }
  
  // change the actual url

  function userslug_set(){
    slug_pretty = slugify(slug_ugly);
    slug_pretty = slug_pretty.substring(0,slug_maxlength);
    
    $('[data-fit-slug-reveal]').text(slug_pretty);
    $('[data-fit-slug-reveal-secret]').val(slug_pretty);

    if (slug_userset == false)
    {
      $('[data-fit-slug-set]').val(slug_pretty);
    }

    // change the auto url:
    slug_url = $('[data-fit-slug-url]').data('fit-slug-url');
    slug_url = (slug_url + slug_pretty);

    $('[data-fit-slug-url]').attr('href', slug_url);
  }

  $("[data-fit-slug-set]").on({
    'change, keyup': function() {
     slug_ugly = $(this).val();
     slug_userset = true;
     userslug_set();
    }
  });  

  // and set it automatically from the user id:

  $("[data-fit-slug-name]").on({
    'change, keyup': function() {
      
      // if it's empty, unset user input
      if (slug_ugly == ''){
        slug_userset = false;
      }

      // user hasn't set it manually:
      if (slug_userset == false)
      {
        // first bit

        if ($('[data-fit-slug-first]').length > 0 && $('[data-fit-slug-first]').val() != ''){
          slug_ugly = $('[data-fit-slug-first]').val();
        }
        // add second if there
        if ($('[data-fit-slug-last]').length > 0 && $('[data-fit-slug-last]').val() != ''){
          slug_ugly = (slug_ugly + $('[data-fit-slug-last]').val());
        }
      }
      
      userslug_set();
    }
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

  // keyup stuff
  $('[data-fit_head_code]').on("keyup change", function(e) {
    console.log($(this).val());
  });


  // ------------------------------------------------------------
  // example modals
  // Just paste this stuff in console to launch modals:

  /*  


  $('#fit_modal_faces_reason'). modal({backdrop: 'static', keyboard: false});
  $('#fit_modal_faces').modal({backdrop: 'static', keyboard: false});
  $('#fit_modal_stuck').modal({backdrop: 'static', keyboard: false});
  $('#fit_modal_nps').modal({backdrop: 'static', keyboard: false});
  $('#fit_modal_text').modal({backdrop: 'static', keyboard: false});
  $('#fit_modal_add_lesson').modal();
  


  if ($('[data-fit_modal_unstoppable]').length > 0)
  {
    $('[data-fit_modal_unstoppable]').modal({
      backdrop: 'static',
      keyboard: false
    });
  }

  if ($('[data-fit_modal]').length > 0)
  {
    $('[data-fit_modal]').modal().show();  
  }  

  */


  // ------------------------------------------------------------
  $('[data-fit_iconselects]').each(function(e) {
    var selected = '';
    var icon_color = '';

    $(this).find('[data-fit_iconselect]').on("click", function(i, e) {

      $(this).siblings('[data-fit_iconselect]').addBack().removeClass('active').addClass('inactive');
      
      $(this).removeClass('inactive').addClass('active');
      $(this).parents('[data-fit_iconselects]').addClass('active');

      icon_color = $(this).find('i').css('color');
      language = $(this).data('fit_iconselect');

      // if there is a why, show it
      if (typeof $(this).data('fit_triggerwhy') !== 'undefined')
      {
        $(this).parents('[data-fit_iconselect_parent]').find('[data-fit_feedback_why]').collapse('show');
      }
      else
      {
        $(this).parents('[data-fit_iconselect_parent]').find('[data-fit_feedback_why]').collapse('hide'); 
      }

      // find and enable the go button, set the colour.
      // we only set the colour and gather info if it ISN'T 'fit_gather',
      // passing fit_gather means get the data and colour from the button
      var gobutton = $(this).parents('[data-fit_iconselect_parent]').find('[data-fit_modal_submit]');

      if (gobutton.data('fit_modal_submit') == 'fit_gather')
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
        .text(gobutton.data('fit_modal_submit'))
        .prop("disabled", false)
        .removeClass('btn-secondary')
        .addClass('btn-primary');
      }

      // wuh oh, what if there's a textarea? Then disable it again until changed

      // if it has a force value....
      if ($('[data-fit_feedback_why_input]').data('fit_modal_force').length > 0){

        gobutton.prop("disabled", true);
        
        $('[data-fit_feedback_why_input]').on({
          'change, keyup': function(e) {
            var val = $(this).val();
            if (val.length > $(this).data('fit_modal_force')){
              gobutton.prop("disabled", false);
            } else {
              gobutton.prop("disabled", true);
            }
          }
        });
      }

      console.log(language);

    });
  });


  $('[data-fit_modal_force]').on({
    'change, keyup': function(e) {
      var val = $(this).val();
      if (val.length > $(this).data('fit_modal_force')){
        $('[data-fit_modal_submit]').prop("disabled", false);
      } else {
        $('[data-fit_modal_submit]').prop("disabled", true);
      }
    }
  });


  // escape to close (27 is escape apparently)
  $(document).keydown(function(e) {
    if (e.keyCode == 27) {
      
      // first check, and only close menu if search or user panel is not on
      if (
          ($('html').hasClass('fit_mobile_menu_active'))
          &&
          (!$('html').hasClass('fit_search_header_active'))
          &&
          (!$('html').hasClass('fit_revealuserpanel'))
        ){
        $('html').removeClass('fit_mobile_menu_active');
      }

      // just the user panel
      if (
          ($('html').hasClass('fit_revealuserpanel'))
        ){
        $('html').removeClass('fit_revealuserpanel');
      }      

      // only remove search if the menu is active
      if (
          ($('html').hasClass('fit_search_header_active'))
        ){
        $('html').removeClass('fit_search_header_active');
      }

    }
  });  


  // ------------------------------------------------------------
  // charts!

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

  function setCookie(name, value) {
    document.cookie = `${name}=${value};expires=Mon, 01 Jan 2970 00:00:00 GMT; path=/`;
  }

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

  function post(url, data, cb) {
    let xhr = new XMLHttpRequest();
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        if (cb) cb(null, xhr, xhr.responseText);
      } else {
        if (cb) cb(xhr.responseText, xhr);
      }
    };
    xhr.open('POST', url);
    var f = new FormData();
    for (let k in data) f.append(k, data[k]);
    if (typeof csrf_token !== 'undefined' && csrf_token) {
      f.append("csrf_token", csrf_token)
    };
    xhr.send(f);
  }

  // Called from the wistia video embed template.
  var _fitz_video = false;
  function fitzVideoReady(video) {
    _fitz_video = video;
    video.bind('end', handleVideoEnd);
    video.bind('percentwatchedchanged', handleVideoProgress);
    video.bind("secondchange", handleVideoTime);
    handleResume(video);
    window._fitz_video = _fitz_video;
  }
  // Export for the Wistia embed.
  window.fitzVideoReady = fitzVideoReady;

  function handleResume(video) {
    if (window.location.search) {
      let m = window.location.search.match(/\bt=(.*)\b/);
      if (m) {
        let t = video.time(parseInt(m[1]));
        video.play();
      }
    }
  }

  function handleVideoEnd() {
    nextSegment(true);  // Autoplay next, stop at lesson end.
  }

  function handleVideoProgress(percent, lastPercent) {
    var id = _fitz_video.data.media.hashedId;
    percent = Math.floor(percent*100);  // Avoid floating point hassles.
    var active_segment = document.querySelector('[data-fit-segment].active');
    var segment_id = active_segment.dataset.fitSegment;
    post('/event/progress', {segment_id:segment_id, percent:percent}, ()=>{});
  }

  function handleVideoTime(seconds) {
    if (seconds % 15 > 0) return;
    var active_segment = document.querySelector('[data-fit-segment].active');
    var segment_id = active_segment.dataset.fitSegment;
    setCookie('resume_segment_place', seconds);
    setCookie('resume_segment_id', segment_id);
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

  delegate('[data-fit-preference-toggle]', 'click', (e, t) => {
    var value = !t.querySelector('input[type=checkbox]').checked;
    var tag = t.dataset.fitPreferenceToggle;
    post(`/preference/${tag}/${(value)?'on':'off'}`);
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

    // Reload the lesson details, if the lesson has changed.
    let resourcePanel = document.querySelector("#fit_lesson_detail[data-fit-active-lesson]");
    if (resourcePanel) {
      let activeLesson = resourcePanel.dataset.fitActiveLesson;
      if (activeLesson != lid) {
        //Change active lesson on nav bar.
        for(let lesson of document.querySelectorAll('.fit_lesson')) {
          lesson.classList.remove('active');
        }
        document.querySelector(`.fit_lesson[data-fit-lesson='${lid}']`)
          .classList.add('active');
        get('/_lesson_resources/'+lid, (e, xhr, data) => {
          if (e) return console.error(e);
          document.querySelector('#fit_lesson_detail').innerHTML = data;
          document.querySelector('#fit_lesson_detail').dataset.fitActiveLesson = lid;
          render_student_chart(studentSel);
        });
      }
    }

    // Change the active state of segment link on the lesson links panel.
    let t = document.querySelector(`[data-fit-segment="${sid}"]`);
    if (!t) return;
    for (let l of document.querySelectorAll('[data-fit-segment].active')) {
      l.classList.remove('active');
    } t.classList.add('active');
  }

  function nextSegment(stopAtLessonEnd) {
    let current = document.querySelector('a[data-fit-segment].active');
    let next = current.nextElementSibling;
    if (!next && !stopAtLessonEnd) {
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
    var lastpages = document.querySelectorAll('[data-fit-lastpage]');
    for (let l in lastpages) l.value = t.href;
    e.preventDefault();
  });

  delegate('[data-fit_toggle_mode]', 'click', (e, t) => {
    e.preventDefault();
    let sel  = t.dataset['fit_toggle_parent'] || 'html';
    let mode = t.dataset['fit_toggle_mode'];
    $(sel).toggleClass(mode);
  });

  delegate('[data-fit_focus]', 'click', (e, t) => {
    e.preventDefault();
    let sel  = t.dataset['fit_focus'];
    $(sel).focus();
  });

  // Pause/resume video on sidebar and after interacting with sidepanel forms.
  var __sidebar_video_paused = false;
  delegate('[data-fit-userpanel]', 'click', (e, t) => {
    if (!_fitz_video) return;
    // The class hasn't changed to its toggled state yet, so the class
    // is kind of flipped.
    var closed = document
                  .documentElement
                  .classList
                  .contains('fit_revealuserpanel');
    if (closed) {
      if (_fitz_video.state() == "playing") {
        _fitz_video.pause();
        __sidebar_video_paused = true;
      }
      // Pop the video time into the form so we can get redirected back.
      let lastpages = document.querySelectorAll('[data-fit-lastpage]');
      let t = Math.floor(_fitz_video.time());
      for (let l of lastpages) {
        l.value = l.value.split('?')[0] + `?t=${t}`;
      }
    } else if (__sidebar_video_paused) {
      _fitz_video.play();
      __sidebar_video_paused = false;
    }
  });

  delegate('textarea[data-course-edit]', 'change', (e, t) => {
    let key = e.target.id;
    let formData = {};
    formData[key] = e.target.value;
    post(e.target.form.action, formData)
  });

  delegate('input[data-course-edit]', 'change', (e, t) => {
    let key = e.target.id;
    let formData = {};
    if (e.target.files) {
      formData['file'] = e.target.files[0];
    }
    formData[key] = e.target.value;
    post(e.target.formAction, formData)
  });

  delegate('[data-fit-perm-group-type]', 'click', (e, t) => {
    var group = t.dataset.fitGroupName;
    let value = '';
    if (group) {
    } else {
      value = (!t.querySelector('input[type=checkbox]').checked)?'on':'off'
    }
    let tag = t.dataset.fitPermGroupType;
    let slug = t.dataset.courseSlug;
    if (value) {
        post(`/course/${slug}/edit/options/${tag}/${value}`);
    }
  });

  delegate('[data-change-slug]', 'click', (e, t) => {
    let slug = t.dataset.courseSlug;
    let value = document.querySelector('#course-slug').value;
    post(`/course/${slug}/edit/slug`, {course_slug: value}, (responseText, xhr) => {
        if (xhr.status == 200) {
            window.location.href = `/course/${JSON.parse(xhr.response)['slug']}/edit`
        } else {
                console.log('DEV: give me some message')
            }
    });
  });

  delegate('a[data-course-edit-remove-teacher]', 'click', (e, t) => {
    let teacherId = e.target.dataset.teacherId;
    let slug = t.dataset.courseSlug;
    let lessonId = e.target.dataset.lessonId;
    let url = "";

    if (lessonId) {
      url = `/course/${slug}/lessons/${lessonId}/teacher/${teacherId}/delete`;
    } else {
      url = `/course/${slug}/edit/remove/teacher/${teacherId}`;
    }

    post(url, {}, (responseText, xhr) => {
        let responseJSON = JSON.parse(xhr.response);
        let alert = $('#add-teacher-alert');
        if (xhr.status == 200) {
            let teacherDiv = $(`#teacher-${responseJSON['teacher_id']}`);
            if (teacherDiv) {
                teacherDiv.remove()
            }
        } else {
                alert.css("display", "block");
                alert.removeClass('alert-success');
                alert.addClass('alert-danger');
                alert.html(responseJSON.message);
            }
    });
  });

  delegate('[data-add-teacher]', 'click', (e, t) => {
    e.preventDefault();
    let email = document.querySelector('#add-teacher-email');
    let slug = t.dataset.courseSlug;
    let lessonId = e.target.dataset.lessonId;
    let url = "";

    if (lessonId) {
      url = `/course/${slug}/lessons/${lessonId}/teacher/add`;
    } else {
      url = `/course/${slug}/edit/add/teacher`;
    }

    post(url, {teacher_email: email.value}, (responseText, xhr) => {
        let alert = $('#add-teacher-alert');
        let responseJSON = JSON.parse(xhr.response);
        alert.css("display", "block");
        if (xhr.status == 400) {
            alert.removeClass('alert-success');
            alert.addClass('alert-danger');
        } else {
            alert.addClass('alert-success');
            alert.removeClass('alert-danger');
            $('#teachers-list').append(responseJSON['teacher'])
        }
        alert.html(responseJSON.message);
    });
  });

  delegate('[data-save-question-answer]', 'click', (e, t) => {
    e.preventDefault();
    let slug = t.dataset.courseSlug;
    let lessonId = t.dataset.lessonId;
    let question = document.querySelector('#lesson-question');
    let answer = document.querySelector('#lesson-question-answer');
    let url = "";

    url = `/course/${slug}/lessons/${lessonId}/qa/add`;

    post(url, {question: question.value, answer: answer.value}, (responseText, xhr) => {
        let responseJSON = JSON.parse(xhr.response);
        if (xhr.status == 400) {
            // DEV: handle wrong action
        } else {
            $('#sortable-list-questions').append(responseJSON['html']);
        }
    });
  });

  delegate('[data-save-question]', 'click', (e, t) => {
    e.preventDefault();
    let slug = t.dataset.courseSlug;
    let lessonId = t.dataset.lessonId;
    let qaId = t.dataset.questionId;
    let question = document.querySelector(`#lesson-question-${qaId}`);
    let answer = document.querySelector(`#lesson-answer-${qaId}`);
    let url = `/course/${slug}/lessons/${lessonId}/qa/${qaId}/edit`;

    post(url, {question: question.value, answer: answer.value}, (responseText, xhr) => {
        let responseJSON = JSON.parse(xhr.response);
        if (xhr.status == 400) {
            // DEV: handle wrong action
        } else {
            // DEV: handle success. Some nice story for a user
        }
    });
  });

  $('#fit_modal_delete').on('show.bs.modal', function(event){
    document.querySelector('#confirm-delete').href = event.relatedTarget.href;
  });

  $('#fit_modal_add_segment').on('show.bs.modal', function(event){
    document.querySelector('#add-video-segment').href = event.relatedTarget.href + event.relatedTarget.dataset['addVideo'];
    document.querySelector('#add-text-segment').href = event.relatedTarget.href + event.relatedTarget.dataset['addText'];
  });

  $('#fit_modal_add_resource_link').on('show.bs.modal', function(event){
    let resourceTitle = $('#resource_title');
    let resourceDescription = $('#fit_wysiwyg_resource');
    let resourceUrl = $('#resource_url');
    let form = $('#add-edit-resource');

    form.attr("action", event.relatedTarget.href);

    if (event.relatedTarget.dataset['resourceId']) {
      let res = get(event.relatedTarget.href, (responseText, xhr) => {
        if (xhr.status == 200) {
            let res = JSON.parse(xhr.response);
            resourceTitle.val(res["title"]);
            resourceDescription.html(res["description"]);
            resourceUrl.val(res["url"]);
            $("input[name=resource_type][value="  + res["type"] + "]").prop("checked", true);
        } else {
        }
          });
    } else {
      resourceTitle.val("");
      resourceDescription.html("");
      resourceUrl.val("");
      $("input[name=resource_type][value=google_drawing]").prop("checked", true)
    }
  });

  delegate('[data-confirm-delete]', 'click', (e, t) => {
    e.preventDefault();
    post(t.href, {}, (responseText, xhr) => {
        if (xhr.status == 200) {
            window.location.href = JSON.parse(xhr.response)['success_url']
        } else {
                // DEV: add some messaging
                console.log(JSON.parse(xhr.response)['message'])
            }
    });
  });

  // ------------------------------------------------------------
  // medium wysiwyg edito stuff

  var autolist = new AutoList();
  var fit_medium = new MediumEditor('#fit_wysiwyg_editor', {
      buttonLabels: 'fontawesome',
      extensions: {
          'autolist': autolist
      }, 
      toolbar: {
          buttons: ['h2', 'h3', 'bold', 'anchor', 'quote', 'unorderedlist','orderedlist']
      }
  });

  delegate('[data-fit-wysiwyg]', 'submit', (e,t) => {
    let p = t.closest('[data-fit-wysiwyg]');
    let preview = p.querySelector('[data-fit-wysiwyg-preview]');
    let textarea = p.querySelector('textarea');
    let mysave = preview.innerHTML;
    textarea.value = mysave;
  });

/* Image upload widget code. */

  function handleImageUpload(t, blob) {
    // We can convert to whatever ext we like, but preserving the original
    // makes things look nicer.
    var ext = ((blob.type || "").indexOf('/') !== -1) ?
            blob.type.split('/').pop() : 'jpeg';
    if (['jpeg', 'jpg', 'png', 'gif'].indexOf(ext) === -1) {
      return false; // Some weird file, we don't want it, whatever.
    }
    var p = t.closest('[data-fit-image-uploader]');
    p.classList.add('fit_upload_cropping');
    var dropzone = p.querySelector('[data-fit-image-dropzone]');
    var input = p.querySelector('[data-fit-image-input]');
    var img = p.querySelector('img');
    var oheight = p.offsetHeight;
    p.style.maxHeight = `${oheight}px`;
    var reader = new FileReader();
    var aspectWidth = parseInt(p.dataset.fitAspectWidth) || 16;
    var aspectHeight = parseInt(p.dataset.fitAspectHeight) || 9;
    reader.onload = (e) => {
      img.onload = () => {
        var save = p.querySelector('[data-fit-save-crop]');
        var cropper = new Cropper(img, {
          viewMode: 3,
          aspectRatio: aspectWidth / aspectHeight,
          dragMode: 'move'
        });
        function saveCroppedImage() {
          cropper.getCroppedCanvas().toBlob((blob) => {
            let formData = {};
            let form = input.closest('form');
            formData['file'] = blob;
            formData[input.name] = `a:/b/c/d/e.f.${ext}`;
            post(form.action, formData);
            p.classList.remove('fit_upload_cropping');
            var reader = new FileReader();
            reader.onload = (e) => {
              img.src = e.target.result;
              // cropper.destroy() doesn't seem to clean this up?
              p.querySelector('.cropper-container').remove();
              img.classList.remove('cropper-hidden');
              save.removeEventListener('click', saveCroppedImage);
            };
            reader.readAsDataURL(blob);
          }, `image/${ext}`);
        }
        save.removeEventListener('click', saveCroppedImage);
        save.addEventListener('click', saveCroppedImage);
      }
      img.src = e.target.result;
    }
    reader.readAsDataURL(blob);
  }

  delegate('[data-fit-image-dropzone]', 'click', (e, t) => {
    e.preventDefault();
    var p = t.closest('[data-fit-image-uploader]');
    var input = p.querySelector('[data-fit-image-input]')
    input.click();
  });

  delegate('[data-fit-image-dropzone]', 'dragenter', (e, t) => {
    e.dataTransfer.setData("text", "somedata");
    var p = t.closest('[data-fit-image-uploader]');
    p.classList.add('fit_upload_dragging');
  });

  delegate('[data-fit-image-dropzone]', 'dragleave', (e, t) => {
    var p = t.closest('[data-fit-image-uploader]');
    p.classList.remove('fit_upload_dragging');
  });

  delegate('[data-fit-image-dropzone]', 'dragover', (e, t) => {
    e.preventDefault();
    var p = t.closest('[data-fit-image-uploader]');
    p.classList.remove('fit_upload_dragging');
  });

  delegate('[data-fit-image-input]', 'change', (e, t) => {
    handleImageUpload(t, t.files[0]);
  })

  delegate('[data-fit-image-dropzone]', 'drop', (e, t) => {
    e.preventDefault();
    var p = t.closest('[data-fit-image-uploader]');
    p.classList.remove('fit_upload_dragging');
    handleImageUpload(t, e.dataTransfer.files[0]);
  });

  // Load the video dynamically when people hit back so the URLs in their
  // URL bar match up with what they're looking at.
  window.addEventListener('popstate', (event) => {
    if (document.location.pathname.match(/^\/course\/\w+\/?$/)) {
      loadSegment(event.state.segment_id);
    }
  });

});
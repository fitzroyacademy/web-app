$( document ).ready(function() {

  // Go team Javascriptz, hack them codez, roxor them boxorz.


  // weird horrible naked tests
  
  $('[data-fit-toggle-coursebar]').click(function(e) {
    e.preventDefault();   
    $('html').toggleClass('fat_coursebar_active');
  });


  // scroll spy for static pages
  $('body').scrollspy({ target: '#scrollspy' })


  // wistia preview thing
  $('[data-fit-wistia-preview]').click(function(e) {
    e.preventDefault();  
    e.stopPropagation();
    // console.log($(this).data('fit-wistia-preview'));

    $('[data-fit-wistia-preview-player]').empty().addClass('active').html('<script src="https://fast.wistia.com/embed/medias/' + $(this).data('fit-wistia-preview') + '.jsonp" async></script><script src="https://fast.wistia.com/assets/external/E-v1.js" async></script><div class="wistia_responsive_padding" style="padding:56.25% 0 0 0;position:relative;"><div class="wistia_responsive_wrapper" style="height:100%;left:0;position:absolute;top:0;width:100%;"><div class="wistia_embed wistia_async_baba5nfzx9 videoFoam=true" style="height:100%;position:relative;width:100%"><div class="wistia_swatch" style="height:100%;left:0;opacity:0;overflow:hidden;position:absolute;top:0;transition:opacity 200ms;width:100%;"><img src="https://fast.wistia.com/embed/medias/baba5nfzx9/swatch" style="filter:blur(5px);height:100%;object-fit:contain;width:100%;" alt="" aria-hidden="true" onload="this.parentNode.style.opacity=1;" /></div></div></div></div>');
  });

  // the dot stuff
  $('[data-fit-fatquote] .dot').click(function(e) {
    e.preventDefault();

    var target = $(this).attr('href');

    $('[data-fit-fatquote] .dot').removeClass('active');
    $('[data-fit-fatquote] .friend').removeClass('active');
    
    $(target).addClass('active');
    $(this).addClass('active');
  });

  $('[data-fit-fatquote] .friend').click(function(e) {
    e.preventDefault();

    var next;

    // if end
    if ($('[data-fit-fatquote] .dot.active').next('.dot').length == 0) {
      next = $('[data-fit-fatquote] .dot:first-child');
    } else {
      next = $('[data-fit-fatquote] .dot.active').next('.dot'); 
    }
    
    var target = $(next).attr('href');

    // erase
    $('[data-fit-fatquote] .dot').removeClass('active');
    $('[data-fit-fatquote] .friend').removeClass('active');

    $(next).addClass('active');
    $(target).addClass('active');

  });
  


  // standard tooltips
  $(function () {
    $('[data-toggle="tooltip"]').tooltip();
  });

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
      let search_term = $(this).val();
      if (search_term.length > 0)
      {
      console.log(search_term);
      }
      else {

      }
    }
  });

  // ------------------------ 
  // fail list sorter:
  $('[data-fit_fail_list]').click(function(e) {
    
    let set = $(this).data('fit_fail_list');

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

  function showAlertSnackbar(text){
    // DEV: need to unpack if text is dict: field_name: message
    Snackbar.show({
      text: text,
      pos: 'bottom-center',
      backgroundColor: '#fff',
      textColor: '#4f5153',
      actionTextColor: '#2793f8',
      customClass: 'fit_snackbar'
    });
  }

  // survey responses stuff
  $('[data-fit_survey_responses] .response').each(function(index, el) {
     let tall = $(this).height();
     if (tall > 180)
     {
      $(this)
      .addClass('truncated')
      .append('<a class="expand"><i class="fal fa-arrow-down"></i> Show more</a>')
      .on('click', function(e) {
        e.preventDefault();
        $(this)
        .removeClass('truncated')
        .addClass('expanded');
      });
     }
  });


  // ------------------------------------------------
  // Will does a hacky "last hit" thing for the tabs in the course player
  $('html.fit_breezy_player .fit_player aside > .fits > .fit_btn[data-toggle="collapse"]').on('click', function(e) {
    // remove the active classes
    $('html.fit_breezy_player .fit_player aside > .fits > .fit_btn[data-toggle="collapse"]').removeClass('active_latest');
    $('html.fit_breezy_player .fit_player aside > .fits > .fit_body.collapse').removeClass('active_latest');
    
    // add just one
    $(this).addClass('active_latest');
    $($(this).attr('href')).addClass('active_latest');
  });

  // get first valid one and show it
  let first_active_latest = $('html.fit_breezy_player .fit_player aside > .fits > [data-toggle="collapse"]:not(.collapsed)').first();
  $(first_active_latest).addClass('active_latest');
  $($(first_active_latest).attr('href')).addClass('active_latest');




  // setting course permissions
  // This uses 'trigger' to find a 'detail' of the same 'type', and toggle active classes
  // NB: Show/hide is done via css, aka [data-data-fit-perm-type]{display: none}

  $('[data-fit-perm-trigger]').on({
    'change': function() {
      let perm = $(this).data('fit-perm-trigger');
      let type = $(this).data('fit-perm-type');
      let slug = $(this).data('course-slug');

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
  // user toggle. don't do it on login so we go to the login page for auth0 always
  $('[data-fit-userpanel]').not('.login').on("click", function(e, i) {
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

  // this happens literally any time any modal is finished buliding and shown

  $(document).on('shown.bs.modal', '.modal', function (e) {
    fancyplace_reset();
  });
  fancyplace_reset();

  // weird RHS modal fun
  $(document).on('show.bs.modal', '.fit_modal_rhs', function (e) {
    $('body').addClass('fit_rhs_modal_active');
  });

  $(document).on('hide.bs.modal', '.fit_modal_rhs', function (e) {
    $('body').removeClass('fit_rhs_modal_active');
  });
  
  



  // ------------------------------------------------------------
  // changing slugs automatically:
  //
  // How to use:
  //
  // Add data-fit-slug-name to the 'name' input on a form.
  // make sure data-fit-slug-first is on the above field or it won't work
  // For login/user names, use these on first/last name fields: data-fit-slug-first and data-fit-slug-last
  // Add data-fit-slug-set to the 'slug' input (i.e. the thing that sets the slug)
  // Add data-fit-slug-reveal to the element that shows the final result
  // Make sure there is a hidden input with data-fit-slug-reveal-secret that actually submits


  // ------------------------------------------------------------
  // variables
  let slug_ugly = '';
  let slug_pretty = '';
  let slug_userset = false;
  let slug_maxlength = 20;
  let slug_url = '';


  // ------------------------------------------------------------
  // check if there's already a slug set
  if ( ($("[data-fit-slug-set]").length > 0) && ($("[data-fit-slug-set]").val().length > 0) ){
    slug_userset = true;
    slug_pretty = $('[data-fit-slug-set]').val();
    slug_ugly = slug_pretty;
  }

  // slugification
  function slugify(string) {
  const a = 'àáäâãåăæçèéëêǵḧìíïîḿńǹñòóöôœøṕŕßśșțùúüûǘẃẍÿź·/_,:;';
  const b = 'aaaaaaaaceeeeghiiiimnnnooooooprssstuuuuuwxyz------';
  const p = new RegExp(a.split('').join('|'), 'g');

  return string.toString().toLowerCase()
    .replace(/\s+/g, '-') // Replace spaces with -
    .replace(p, c => b.charAt(a.indexOf(c))) // Replace special characters
    .replace(/&/g, '-and-') // Replace & with 'and'
    .replace(/[^\w\-]+/g, '') // Remove all non-word characters
    .replace(/\-\-+/g, '-') // Replace multiple - with single -
    .replace(/^-+/, '') // Trim - from start of text
    .replace(/-+$/, ''); // Trim - from end of text
  }
  
  // change the actual url

  function fit_slug_set(){
    slug_pretty = slugify(slug_ugly);
    slug_pretty = slug_pretty.substring(0,slug_maxlength);
    
    $('[data-fit-slug-reveal]').text(slug_pretty);
    $('[data-fit-slug-reveal-secret]').val(slug_pretty);

    if (slug_userset == false)
    {
      $('[data-fit-slug-set]').val(slug_pretty);
    }

    // change the auto url:
    let slugUrlElement = $('[data-fit-slug-url]');
    slug_url = slugUrlElement.data('fit-slug-url');
    slug_url = (slug_url + slug_pretty);

    slugUrlElement.attr('href', slug_url);
  }

  // user manually sets the slug
  $("[data-fit-slug-set]").on({
    'change, keyup': function() {
     slug_ugly = $(this).val();
     slug_userset = true;
     fit_slug_set();
    }
  });


  // ------------------------------------------------------------
  // colour the progress bars
  $('.progress-bar').each(function(index, el) {

    // find the percentage width
    let pwidth = $(this).width() / $(this).parent().width() * 100;
     
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

  // escape to close (27 is escape apparently)
  $(document).keydown(function(e) {
    if (e.keyCode == 27) {
      
      // first check, and only close menu if search or user panel is not on
      let htmlElement = $('html');
      if (
          (htmlElement.hasClass('fit_mobile_menu_active'))
          &&
          (!htmlElement.hasClass('fit_search_header_active'))
          &&
          (!htmlElement.hasClass('fit_revealuserpanel'))
        ){
        htmlElement.removeClass('fit_mobile_menu_active');
      }

      // just the user panel
      if (
          (htmlElement.hasClass('fit_revealuserpanel'))
        ){
        htmlElement.removeClass('fit_revealuserpanel');
      }      

      // only remove search if the menu is active
      if (
          (htmlElement.hasClass('fit_search_header_active'))
        ){
        htmlElement.removeClass('fit_search_header_active');
      }

    }
  });  


  // ------------------------------------------------------------
  // charts!

  let chart = null;
  function render_student_chart(student_selector) {

    let colors = ['#333'];

    let lessonDetails = document.querySelectorAll('[data-fit-lesson-details]');
    let classAverage = [];
    for (let l of lessonDetails) {
      classAverage.push(l.dataset.fitAvgProgress);
    }

    let series = [
      {name: 'Class Average', data: classAverage},
    ];

    let students = document.querySelectorAll(student_selector);

    for (let s of students) {
      //colors.push(s.dataset.fitChartColor);
      colors.push('#'+(Math.random()*0xFFFFFF<<0).toString(16));
      series.push({
        name: s.dataset.fitStudentName,
        data: s.dataset.fitStudentCompletion.split(';').map((s) => parseInt(s))
      });
    }

    let options = {
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
    };

    if ($('#fit_chart').length > 0) {
      if (!chart) {
        chart = new ApexCharts(document.querySelector("#fit_chart"), options);
        chart.render();
      }
      chart.updateOptions({colors: colors});
      chart.updateSeries(series);
    }

  }

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
    let f = data;
    if (!(data instanceof FormData)) {
      f = new FormData();
      for (let k in data) f.append(k, data[k]);
    }
    if (typeof csrf_token !== 'undefined' && csrf_token) {
      f.append("csrf_token", csrf_token);
    };
    xhr.send(f);
  }

  // Called from the wistia video embed template.
  let _fitz_video = false;
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

  let _lastRecordedPercent = 0;
  function handleVideoProgress(percent, lastPercent) {
    percent = Math.floor(percent*100);  // Avoid floating point hassles.
    // Don't choke the server with minute progress changes.
    if (percent - _lastRecordedPercent <= 1) return;
    _lastRecordedPercent = percent;
    let id = _fitz_video.data.media.hashedId;
    let active_segments = document.querySelectorAll('[data-fit-segment].active');
    let segment_id = active_segments[0].dataset.fitSegment;
    post('/event/progress', {segment_id:segment_id, percent:percent}, (e, xhr, data)=>{
      let d = JSON.parse(data);
      let s = d.user_status;
      if (!s) return;
      for (let l of active_segments) {
        for (let status of ['touched', 'completed', 'locked']) {
          if (s !== status) l.classList.remove(status);
        }
        l.classList.add(s);
      }
    });
  }

  function handleVideoTime(seconds) {
    if (seconds % 15 > 0) return;
    let active_segment = document.querySelector('[data-fit-segment].active');
    let segment_id = active_segment.dataset.fitSegment;
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
    if (matches.length === 0) {
      return console.warn('No matching data panels for', sel);
    } 
    get(p, (e, xhr, data) => {
      if (e) console.error(e);
      for (let el of matches) el.innerHTML = data;
    });
  });

  delegate('[data-fit-preference-toggle]', 'click', (e, t) => {
    let value = !t.querySelector('input[type=checkbox]').checked;
    let tag = t.dataset.fitPreferenceToggle;
    post(`/preference/${tag}/${(value)?'on':'off'}`, {}, (e, xhr, data) => {
      if (xhr.status === 200) {
        showAlertSnackbar("Settings saved.")
      } else {
        showAlertSnackbar("An error has occurred.")
      }
    });

  });

  let studentSel = '[data-fit-student-completion].active';
  delegate('[data-fit-student-completion]', 'click', (e, t) => {
    t.classList.toggle('active');
    e.preventDefault();
    render_student_chart(studentSel);
  });
  render_student_chart(studentSel);

  function lockSegments(locked_segments, fromId, hard=false) {
    let lock = false;
    let segments = document.querySelectorAll('a[data-fit-segment-link]');
    let segId = null;
    for (let i = 0; i < segments.length; i++) {
      let seg = segments[i];
      seg.classList.remove("locked");
      segId = parseInt(seg.dataset["fitSegment"]);
      if (locked_segments.includes(segId)) {
        if (fromId != segId && !hard) {
            seg.classList.add("locked");
            seg.classList.remove("accessible");
        }
      }
    }

  }

  function loadSegment(sid, lid) {
    // Load the video.
    get('/_segment/'+sid+'.json', (e, xhr, data) => {
      let unlockedPane = document.querySelector("[data-fit-vidya-unlocked]");
      let lockedPane = document.querySelector("[data-fit-vidya-locked]");
      let dataContainer;
      if (e) console.error(e);
      data = JSON.parse(data);
      if (!data.locked) {
        unlockedPane.style.display = "block";
        lockedPane.style.display = "none";
        activatePane(data['segment_type'] + "_content", "segment_display_content");
        if (data['segment_type'] === 'video') {
          _fitz_video.replaceWith(data.active_segment.external_id);
          _fitz_video.play();
        } else if (data['segment_type'] === 'text') {
          dataContainer = document.querySelector('[data-fit-pane-detail="text_content"]');
          dataContainer.innerHTML = "";
          let parser = new DOMParser();
          let html = parser.parseFromString(data['html'], 'text/html');
          dataContainer.append(html.body.firstChild);
        } else if (data['segment_type'] === 'survey') {
          dataContainer = document.querySelector('[data-fit-pane-detail="survey_content"]');
          dataContainer.innerHTML = "";
          let parser = new DOMParser();
          let html = parser.parseFromString(data['html'], 'text/html');
          dataContainer.append(html.body);
        } else {
          unlockedPane.style.display = "none";
          lockedPane.style.display = "block";
        }
      }


      if (data["barrier_id"]) {
        let hard = false;
        if (data["barrier_type"] == "hard_barrier") {
          hard = true
        }
        lockSegments(data["locked_segments"], data["barrier_id"], hard)
      }
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
    let t = document.querySelectorAll(`[data-fit-segment="${sid}"]`);
    if (t.length == 0) return;
    for (let l of document.querySelectorAll('[data-fit-segment].active')) {
      l.classList.remove('active');
    }
    for (let l of t) {
      l.classList.add('active');
    }
  }

  function nextSegment(stopAtLessonEnd) {
    _lastRecordedPercent = 0;  // This needs a refactor.
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
    let lastpages = document.querySelectorAll('[data-fit-lastpage]');
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
  let __sidebar_video_paused = false;
  delegate('[data-fit-userpanel]', 'click', (e, t) => {
    if (!_fitz_video) return;
    // The class hasn't changed to its toggled state yet, so the class
    // is kind of flipped.
    let closed = document
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

  delegate('textarea[data-course-edit],textarea[data-institute-edit]', 'change', (e, t) => {
    let key = e.target.id;
    let formData = {};
    formData[key] = e.target.value;
    post(e.target.form.action, formData)
  });

  // DEV: make it work
  // delegate('#further_reading', 'change', (e, t) => {
  //   console.log('Magic should happen here');
  //
  // });

  delegate('input[data-course-edit],input[data-fit-lesson-edit],' +
      'input[data-institute-edit],input[data-fit-user-edit]', 'change', (e, t) => {
    let key = e.target.id;
    let formData = {};
    if (e.target.files) {
      formData['file'] = e.target.files[0];
    }
    formData[key] = e.target.value;
    post(e.target.formAction, formData, (responseText, xhr) => {
        let responseJSON = JSON.parse(xhr.response);
        if (xhr.status === 200) {
            // do something clever
        } else {
            showAlertSnackbar(responseJSON["message"])
         }
    })
  });

  delegate('[data-fit-perm-group-type]', 'click', (e, t) => {
    let group = t.dataset.fitGroupName;
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
    e.preventDefault();
    let courseSlug = t.dataset.courseSlug;
    let instituteSlug = t.dataset.courseSlug;
    let p = t.closest('[data-fit-change-slug]');
    let value = p.querySelector('[data-slug-value]').value;
    let url = courseSlug ? `/course/${courseSlug}/edit/slug` : '/institute/edit/slug';

    post(url, {slug: value}, (responseText, xhr) => {
        if (xhr.status === 200) {
            window.location.href = JSON.parse(xhr.response)['redirect_url']
        } else {
                console.log('DEV: give me some message')
            }
    });
  });

  delegate('a[data-remove-user]', 'click', (e, t) => {
    let userId = e.target.dataset.userId;
    let courseSlug = t.dataset.courseSlug;
    let userType = t.dataset.userType;
    let instituteSlug = t.dataset.instituteSlug;
    let url = "";

    if (courseSlug) {
        let lessonId = e.target.dataset.lessonId;
        if (lessonId) {
            url = `/course/${courseSlug}/lessons/${lessonId}/teacher/${userId}/delete`;
        } else {
            url = `/course/${courseSlug}/edit/remove/teacher/${userId}`;
        }
    } else {
      url = `/institute/edit/user/remove/${userId}/${userType}`
    }

    post(url, {}, (responseText, xhr) => {
        let responseJSON = JSON.parse(xhr.response);

        let alert = document.querySelector(`[data-${userType}-action-alert]`);
        alert.style.display = "none";
        if (xhr.status === 200) {
            let teacherDiv = t.closest('[data-fit-user]');
            if (teacherDiv) {
                teacherDiv.remove()
            }
        } else {
                alert.style.display = "block";
                alert.classList.remove('alert-success');
                alert.classList.add('alert-danger');
                alert.innerHTML = responseJSON.message;
            }
    });
  });

  delegate('[data-add-user]', 'click', (e, t) => {
    e.preventDefault();

    let p = t.closest('[data-fit-add-user]');
    let email = p.querySelector('[data-user-email]');
    let courseSlug = t.dataset.courseSlug;
    let instituteSlug = t.dataset.instituteSlug;
    let url = "";
    let userType = t.dataset.userType;

    if (courseSlug){
      let lessonId = e.target.dataset.lessonId;
      if (lessonId) {
        url = `/course/${courseSlug}/lessons/${lessonId}/teacher/add`;
      } else {
        url = `/course/${courseSlug}/edit/add/teacher`;
      }
    } else {
      url = `/institute/edit/add/${userType}`
    }


    post(url, {teacher_email: email.value}, (responseText, xhr) => {
        let alert = document.querySelector(`[data-${userType}-action-alert]`);
        let responseJSON = JSON.parse(xhr.response);
        alert.style.display = "block";
        if (xhr.status === 400) {
            alert.classList.remove('alert-success');
            alert.classList.add('alert-danger');
        } else {
            alert.classList.add('alert-success');
            alert.classList.remove('alert-danger');
            let usersList = p.querySelector('[data-users-list]');
            usersList.innerHTML = usersList.innerHTML + responseJSON['teacher'];
        }
        alert.innerHTML = responseJSON.message;
    });
  });

  delegate('[data-fit-user-save]', 'click', (e, t) => {
    e.preventDefault();
    let form = t.closest('form');
    let formData = new FormData(form);
    let url = form.action;

    let data = {
      "first_name": formData.get("first_name"),
      "last_name": formData.get("last_name"),
      "username": formData.get("username"),
      "email": formData.get("email"),
    };
    post(url, data, (responseText, xhr) => {
        let res = JSON.parse(xhr.response);
        if ("errors" in res && res["errors"].length > 0){
          for (let i = 0; i < res["errors"].length; i++) {
            showAlertSnackbar(res["errors"][i])
          }
        } else {
          showAlertSnackbar(res["message"]);
        }
    });
  });

  delegate('[data-save-question-answer]', 'click', (e, t) => {
    e.preventDefault();
    let slug = t.dataset.courseSlug;
    let lessonId = t.dataset.lessonId;
    let question = document.querySelector('[data-fit-lesson-question]');
    let answer = document.querySelector('[data-fit-lesson-question-answer]');
    let url = `/course/${slug}/lessons/${lessonId}/qa/add`;

    post(url, {question: question.value, answer: answer.value}, (responseText, xhr) => {
        let responseJSON = JSON.parse(xhr.response);
        if (xhr.status === 400) {
            showAlertSnackbar(responseJSON['message'])
        } else if (xhr.status === 200) {
            $('[data-fit-sortable-list-questions]').append(responseJSON['html']);
            showAlertSnackbar(responseJSON['message'])
        } else {
          showAlertSnackbar("Unknown error")
        }
    });
  });

  delegate('[data-save-question]', 'click', (e, t) => {
    e.preventDefault();
    let slug = t.dataset.courseSlug;
    let lessonId = t.dataset.lessonId;
    let qaId = t.dataset.questionId;
    let container = t.closest('[data-fit-qa-container]');
    let question = container.querySelector('input');
    let answer = container.querySelector("textarea");
    let url = `/course/${slug}/lessons/${lessonId}/qa/${qaId}/edit`;

    post(url, {question: question.value, answer: answer.value}, (responseText, xhr) => {
        let responseJSON = JSON.parse(xhr.response);
        if (xhr.status === 400 || xhr.status === 200) {
            showAlertSnackbar(responseJSON['message'])
        } else {
            showAlertSnackbar("Unknown error")
        }
    });
  });

  $('#fit_modal_delete').on('show.bs.modal', function(event){
    document.querySelector('[data-confirm-delete]').href = event.relatedTarget.href;
  });

  delegate('[data-fit-add-lesson]', 'click', (e, t) => {
    $('[data-fit-add-lesson-choice]').modal('hide');
    $('[data-fit-modal-add-lesson]').modal('show');
  });

  function getModalSegment(courseSlug, lessonId, segmentType, segmentId=null) {
    let modalObj = $(`[data-fit-add-${segmentType}-segment-modal]`);
    if (modalObj.length === 0) {
      get(`/course/${courseSlug}/lessons/${lessonId}/segments/${segmentType}`, (responseText, xhr) => {
        let res = JSON.parse(xhr.response);
        if (xhr.status === 400) {
          showAlertSnackbar(res["message"]);
        } else if (xhr.status === 200) {
          let parser = new DOMParser();
          let html = parser.parseFromString(res["html"], 'text/html');
          document.body.append(html.body.firstChild);
          modalObj = $(`[data-fit-add-${segmentType}-segment-modal]`);
          if (segmentId) {
            addSegmentModalContent(modalObj[0], courseSlug, lessonId, segmentId);
          }
          modalObj.modal('show');
        } else {
          showAlertSnackbar("Something went wrong");
        }
      })
    }
    return modalObj
  }

  function addSegmentModalContent(modal, courseSlug, lessonId, segmentId) {
    get(`/course/${courseSlug}/lessons/${lessonId}/segments/${segmentId}`,
            (responseText, xhr) => {
              if (xhr.status === 200) {
                let res = JSON.parse(xhr.response);
                modal.querySelector('#segment_name').value = res['title'];
                if (res['segment_type'] === 'video') {
                  modal.querySelector('#segment_url').value = res['segment_url'];
                  if (res['video_type']){
                    modal.querySelector(`#${res['video_type']}`).checked = true;
                  }
                  if (res['permission']){
                    modal.querySelector(`#${res['permission']}`).checked = true;
                  }
                } else if (res['segment_type'] === 'text') {
                  modal.querySelector('#fit_wysiwyg_editor').innerHTML = res['text'];
                } else if (res['segment_type'] === 'survey') {
                  if (res['permission']){
                    modal.querySelector(`#${res['permission']}`).checked = true;
                  }
                  let choice_questions = res['survey']['choice_questions'] || null;
                  function updateSurvey(partialDict) {
                    Object.entries(partialDict).forEach(([key, value]) => {
                    if (typeof value === 'boolean') {
                      modal.querySelector(`input[name=${key}]`).checked = value;
                    } else {
                      modal.querySelector(`input[name=${key}]`).value = value;
                    }
                  });
                  }

                  if (choice_questions) {
                      delete res['survey']['choice_questions'];
                    for (let question of choice_questions) {
                      updateSurvey(question)
                    }
                  }

                  // activate proper survey pane
                  modal.querySelector(`#${res['survey_id']}`).checked = true;
                  activatePane(res['survey_id'], "survey_type");
                  updateSurvey(res['survey'])

                }
                modal.querySelector('[data-fit-add-edit-segment-form]').dataset['fitSegmentId'] = segmentId;
              } else {
                showAlertSnackbar("Oh snap, something went wrong. Try again.")
              }
        });
  }

  delegate('[data-fit-edit-segment-action]', 'click', (e, t) => {
    let segmentType = t.dataset['fitSegmentType'];
    let segmentId = t.dataset['fitSegmentId'];
    let container = t.closest('[data-fit-list-elements-container]');
    let courseSlug = container.dataset['fitCourseSlug'];
    let lessonId = container.dataset['fitLessonId'];
    let modalObj = $(`[data-fit-add-${segmentType}-segment-modal]`);
    if (modalObj.length > 0) {
      addSegmentModalContent(modalObj[0], courseSlug, lessonId, segmentId);
      modalObj.modal('show');
    } else {
      getModalSegment(courseSlug, lessonId, segmentType, segmentId);
    }
  });

  delegate('[data-fit-add-edit-segment]', 'click', (e, t) => {
      $('[data-fit-modal-add-segment]').modal('hide');
      let segmentType = t.dataset['fitSegmentType'];
      let wrapperModal = t.closest("[data-fit-modal-add-segment]");
      let courseSlug = wrapperModal.dataset['fitCourseSlug'];
      let lessonId = wrapperModal.dataset['fitLessonId'];
      let modalObj = $(`[data-fit-add-${segmentType}-segment-modal]`);

      if (modalObj.length > 0) {
        if (segmentType === 'text') {
          modalObj[0].querySelector('[data-fit-segment-name]').value = "";
          modalObj[0].querySelector('[data-fit-wysiwyg-preview]').innerHTML = "";
        } else if (segmentType === 'survey') {
          // do some stuff here
        } else {
          modalObj[0].querySelector('[data-fit-segment-name]').value = "";
          modalObj[0].querySelector('[data-fit-segment-url]').value = "";
          modalObj[0].querySelector('[data-fit-segment-standard]').checked = true;
          modalObj[0].querySelector('[data-fit-segment-normal]').checked = true;
        }
        modalObj.modal('show');
        modalObj[0].querySelector('[data-fit-add-edit-segment-form]').dataset['fitSegmentId'] = "";
      } else {
        getModalSegment(courseSlug, lessonId, segmentType)
      }

  });

  delegate('[data-fit-add-intro-submit]', 'click', (e, t) => {
    let form = t.closest('form');
    let formData = new FormData(form);
    let data = {"segment_url": formData.get("segment_url"), "intro_lesson": ""};

    post(form.action, data, (responseText, xhr) => {
        let res = JSON.parse(xhr.response);
        if (xhr.status === 200) {
            showAlertSnackbar(res["message"]);
            $('[data-fit-add-edit-segment-modal]').modal('hide');
            if ("html" in res) {
              let container = document.querySelector('[data-fit-sortable-list-with-intro-element]');
              container.innerHTML = res['html'] + container.innerHTML;
              document.querySelector('[data-fit-add-intro]').style.display = "none";
            }
        } else {
                showAlertSnackbar(res['message'])
            }
    });

  });

  delegate('[data-fit-segment-add-edit-submit]', 'click', (e, t) => {
    e.preventDefault();
    let form = t.closest('form');
    let formData = new FormData(form);
    let segmentId = form.dataset['fitSegmentId'];
    let segmentType = form.dataset['fitSegmentType'];
    let courseSlug = form.dataset['fitCourseSlug'];
    let lessonId = form.dataset['fitLessonId'];
    let previewWysiwyg = form.querySelector('[data-fit-wysiwyg-preview]');
    let description = "";
    let url = '';
    if (previewWysiwyg) {
      description = previewWysiwyg.innerHTML;
    }

    if (segmentId) {
      url = `/course/${courseSlug}/lessons/${lessonId}/segments/${segmentId}/edit`
    } else {
      url = `/course/${courseSlug}/lessons/${lessonId}/segments/add/${segmentType}`
    }

    let data = {};
    for (let key of formData.keys()) {
      data[key] = formData.get(key)
    }
    data['text_segment_content'] = description;

    post(url, data, (responseText, xhr) => {
        let res = JSON.parse(xhr.response);
        if (xhr.status === 200) {
          showAlertSnackbar(res["message"]);
          $('[data-fit-add-edit-segment-modal]').modal('hide');

          if ("html" in res) {
            if (segmentId) {
                let segmentEl = document.querySelector(`[data-segment-el-id-${res['id']}]`);
                segmentEl.outerHTML = res['html'];
            } else {
                let container = document.querySelector('[data-fit-sortable-list]');
                container.innerHTML = container.innerHTML + res['html'];
            }
          }
        } else {
          showAlertSnackbar(res['message']);
        }
    });

  });

  $('#fit_modal_add_resource_link').on('show.bs.modal', function(event){
    let form = $('[data-fit-add-edit-resource-form ]')[0];
    let resourceTitle = form.querySelector('[data-fit-resource-title]');
    let resourceDescription = form.querySelector('[data-fit-wysiwyg-preview]');
    let resourceUrl = form.querySelector('[data-fit-resource-url]');
    let resourceFeatured = form.querySelector('[data-fit-resource-featured]');

    form.action = event.relatedTarget.href;
    if (event.relatedTarget.dataset['resourceId']) {
      get(event.relatedTarget.href, (responseText, xhr) => {
        if (xhr.status === 200) {
            let res = JSON.parse(xhr.response);
            resourceTitle.value = res["title"];
            resourceDescription.innerHTML = res["description"];
            resourceUrl.value = res["url"];
            resourceFeatured.checked = res["featured"];
            $("input[name=resource_type][value="  + res["type"] + "]").prop("checked", true);
        } else {
          showAlertSnackbar("Failed retrieving resource data")
        }
          });
    } else {
      resourceTitle.value = "";
      resourceDescription.innerHTML = "";
      resourceUrl.value = "";
      $("input[name=resource_type][value=google_drawing]").prop("checked", true)
    }
  });

  delegate('[data-fit-add-edit-resource-form]', 'submit', (e, t) => {
    e.preventDefault();
    let form = t.closest('[data-fit-add-edit-resource-form ]');
    let formData = new FormData(form);
    let previewWysiwyg = form.querySelector('[data-fit-wysiwyg-preview]');
    let data = {
      resource_url: formData.get('resource_url'),
      resource_title: formData.get('resource_title'),
      resource_description: previewWysiwyg.innerHTML,
      resource_featured: formData.get('resource_featured'),
      resource_type: formData.get('resource_type')
    };
    post(form.action, data, (responseText, xhr) => {
        let res = JSON.parse(xhr.response);
        if (xhr.status === 200) {
            showAlertSnackbar(res["message"]);
            $('[data-fit-modal-add-resource-link]').modal('hide');
            if ("html" in res) {
              let resourceEl = document.querySelector(`[data-resource-el-id-${res['id']}]`);
              if (resourceEl) {
                resourceEl.outerHTML = res['html'];
              } else {
                  let container = document.querySelector('[data-fit-sortable-list-resources]');
                  container.innerHTML = container.innerHTML + res['html'];
              }
              showAlertSnackbar(res['message'])
            }
        } else if (xhr.status === 400) {
            showAlertSnackbar(res['message'])
        } else {
            showAlertSnackbar("Unknown error")
        }
    });
  });

  delegate('[data-confirm-delete]', 'click', (e, t) => {
    e.preventDefault();
    post(t.href, {}, (responseText, xhr) => {
        if (xhr.status === 200) {
            window.location.href = JSON.parse(xhr.response)['success_url']
        } else {
                showAlertSnackbar(JSON.parse(xhr.response)['message'])
            }
    });
  });

  // ------------------------------------------------------------
  // medium wysiwyg edito stuff


  delegate('[data-fit-wysiwyg]', 'submit', (e,t) => {
    let p = t.closest('[data-fit-wysiwyg]');
    let preview = p.querySelector('[data-fit-wysiwyg-preview]');
    let textarea = p.querySelector('textarea');
    textarea.value = preview.innerHTML;
  });

  delegate("[data-fit-wysiwyg-preview]", 'click', (e, t) => {
    let form = t.closest('form');
    let p = t.closest('[data-fit-wysiwyg]');
    if (p.fit_editor) return;
    // Initialize the editor.
    let autolist = new AutoList();
    let preview  = p.querySelector('[data-fit-wysiwyg-preview]');
    let textarea  = p.querySelector('[data-fit-wysiwyg-raw]');
    let buttons = (p.dataset.fitWysiwygButtons || "").trim();
    let toolbar = (buttons) ? {buttons: buttons.split(/\s/)} : null;
    let editor = new MediumEditor(preview, {
      buttonLabels: 'fontawesome',
      extensions: {'autolist': autolist },
      toolbar: toolbar
    });
    editor.subscribe('editableInput', () => {
      textarea.textContent = preview.innerHTML;
      post(form.action, new FormData(form));
    });
    p.fit_editor = editor;
  });

/* Image upload widget code. */

  function handleImageUpload(t, blob) {
    // We can convert to whatever ext we like, but preserving the original
    // makes things look nicer.
    let ext = ((blob.type || "").indexOf('/') !== -1) ?
            blob.type.split('/').pop() : 'jpeg';
    if (['jpeg', 'jpg', 'png', 'gif'].indexOf(ext) === -1) {
      return false; // Some weird file, we don't want it, whatever.
    }
    let p = t.closest('[data-fit-image-uploader]');
    p.classList.add('fit_upload_cropping');
    let input = p.querySelector('[data-fit-image-input]');
    let img = p.querySelector('img');
    let oheight = p.offsetHeight;
    p.style.maxHeight = `${oheight}px`;
    let reader = new FileReader();
    let aspectWidth = parseInt(p.dataset.fitAspectWidth) || 16;
    let aspectHeight = parseInt(p.dataset.fitAspectHeight) || 9;
    reader.onload = (e) => {
      img.onload = () => {
        let save = p.querySelector('[data-fit-save-crop]');
        let cropper = new Cropper(img, {
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
            post(form.action, formData, (responseText, xhr) => {
              let res = JSON.parse(xhr.response);
              if (xhr.status === 400) {
                if ("errors" in res && res["errors"].length > 0) {
                  for (let i = 0; i < res["errors"].length; i++) {
                    showAlertSnackbar(res["errors"][i])
                  }} else if ("message" in res) {
                  showAlertSnackbar(res["message"])
                }
              }
            });
            p.classList.remove('fit_upload_cropping');
            let reader = new FileReader();
            reader.onload = (e) => {
              img.onload = null;
              img.src = e.target.result;
              cropper.destroy();
              save.removeEventListener('click', saveCroppedImage);
            };
            reader.readAsDataURL(blob);
          }, `image/${ext}`);
        }
        save.removeEventListener('click', saveCroppedImage);
        save.addEventListener('click', saveCroppedImage);
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(blob);
  }

  delegate('[data-fit-image-dropzone]', 'click', (e, t) => {
    e.preventDefault();
    let p = t.closest('[data-fit-image-uploader]');
    let input = p.querySelector('[data-fit-image-input]');
    input.click();
  });

  delegate('[data-fit-image-dropzone]', 'dragenter', (e, t) => {
    e.dataTransfer.setData("text", "somedata");
    let p = t.closest('[data-fit-image-uploader]');
    p.classList.add('fit_upload_dragging');
  });

  delegate('[data-fit-image-dropzone]', 'dragleave', (e, t) => {
    let p = t.closest('[data-fit-image-uploader]');
    p.classList.remove('fit_upload_dragging');
  });

  delegate('[data-fit-image-dropzone]', 'dragover', (e, t) => {
    e.preventDefault();
    let p = t.closest('[data-fit-image-uploader]');
    p.classList.remove('fit_upload_dragging');
  });

  delegate('[data-fit-image-input]', 'change', (e, t) => {
    handleImageUpload(t, t.files[0]);
  });

  delegate('[data-fit-image-dropzone]', 'drop', (e, t) => {
    e.preventDefault();
    let p = t.closest('[data-fit-image-uploader]');
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

  delegate('[data-fit-custom-setting]', 'click', (e, t) => {
    let key = t.dataset['fitCustomSettingsKey'];
    let value = t.dataset['fitCustomSettingsValue'];
    post('/user/settings', {key: key, value: value}, (responseText, xhr) => {
        if (xhr.status === 200) {
          // DEV: do some cool stuff with setting
          showAlertSnackbar("Setting added")
        } else {
          showAlertSnackbar(JSON.parse(xhr.response)['message'])
        }
    })
  });

  function activatePane(pane, paneType) {
    $('[data-fit-pane-detail][data-fit-pane-type="' + paneType + '"]').removeClass('active');
    $('[data-fit-pane-detail=' + pane + ']').addClass('active');
  }

  delegate('[data-fit-toggl-pane-trigger]', 'click', (e, t) => {
    let pane = (t.value ? t.value : t.dataset['fitPaneValue']);
    let type = t.dataset['fitPaneType'];
    activatePane(pane, type)
  });


  delegate('[data-fit_iconselect]', 'click', function(e, t) {
    let icon_color = '';
    let iconselectParentContainer = t.closest('[data-fit_iconselects]');
    let parentContainer = t.closest('[data-fit_iconselect_parent]');
    iconselectParentContainer.classList.add('active');
    let siblings = iconselectParentContainer.querySelectorAll('[data-fit_iconselect]');
    for (let i = 0; i < siblings.length; ++i) {
       siblings[i].classList.add('inactive');
       siblings[i].classList.remove('active');
    }

    t.classList.remove('inactive');
    t.classList.add('active');

    icon_color = window.getComputedStyle(t.querySelector('i')).getPropertyValue("color");
    let language = t.dataset['fit_iconselect'];
    let whyContainer = parentContainer.querySelector('[data-fit_feedback_why]');
    let freeTextRequired = ('fit_triggerwhy' in t.dataset);
    let forceResponse = ('fit_force_response' in t.dataset);
      // if there is a why, show it
      if (freeTextRequired)
      {
        $(whyContainer).collapse('show');
      }
      else
      {
        $(whyContainer).collapse('hide');
      }

      // find and enable the go button, set the colour.
      // we only set the colour and gather info if it ISN'T 'fit_gather',
      // passing fit_gather means get the data and colour from the button
      let gobutton = parentContainer.querySelector('[data-fit_iconselects_submit]');

      if (gobutton) {
        // do something fancy if it's a 'fit_gather' button:
        if (gobutton.dataset['fit_iconselects_submit'] === 'fit_gather') {
          gobutton.innerHTML = language;
          gobutton.disabled = freeTextRequired;
          gobutton.style.backgroundColor = icon_color;
        } else {
          if (freeTextRequired) {
            gobutton.innerHTML = gobutton.dataset['fit_iconselects_free_text_required'];
            gobutton.disabled = true;
            gobutton.classList.add('btn-secondary');
            gobutton.classList.remove('btn-primary')
          } else {
            gobutton.innerHTML = gobutton.dataset['fit_iconselects_submit'];
            gobutton.disabled = false;
            gobutton.classList.remove('btn-secondary');
            gobutton.classList.add('btn-primary')
          }
        }
      }

      // wuh oh, what if there's a textarea? Then disable it again until changed
      // if it has a force value....
      if (freeTextRequired) {
        let freeTextInput = $('[data-fit_feedback_why_input]').value;
        if (freeTextInput) {
          if (freeTextInput.value.length < $('[data-fit_survey_force]').data('fit_survey_force')) {
            gobutton.setAttribute("disabled", true);
          }
        }
      }

    });

  delegate('[data-fit_survey_force]', 'keyup', (e, t) => {
      // DEV: write this without jQuery ?
      let gobutton = $('[data-fit_iconselects_submit]');
      let target = $(t);
      let vallength = target.val().length;

      // if the length is good:
      if (vallength > target.data('fit_survey_force')){
        if (gobutton.data('fit_iconselects_submit') === 'fit_gather')
        {
          gobutton.prop("disabled", false);
        }
        else {
          gobutton
          .text(gobutton.data('fit_iconselects_submit'))
          .prop("disabled", false)
          .removeClass('btn-secondary')
          .addClass('btn-primary');
        }
      }

      // otherwise disable it
      else {
        if (gobutton.data('fit_iconselects_submit') === 'fit_gather')
        {
          gobutton.prop("disabled", true);
        }
        else {
          gobutton
          .text(gobutton.data('fit_iconselects_free_text_required'))
          .prop("disabled", true)
          .addClass('btn-secondary')
          .removeClass('btn-primary');
        }
      }

      // set the counter
      $('[data-fit_survey_force_counter]').text(vallength);
  });

  delegate('[data-fit-submit-text-segment]', 'click', (e, t) => {
    post('/event/progress', {percent: 100, segment_id: t.dataset['fitSegmentId']});
    nextSegment(true)
  });

  delegate('[data-fit-submit-survey-segment]', 'click', (e, t) => {
    let surveyContainer = t.closest('[data-fit_iconselect_parent]');
    let choicesContainer = surveyContainer.querySelector('[data-fit_iconselects');
    let freeTextArea = surveyContainer.querySelector('[data-fit_feedback_why_input]');
    let freeText = '';
    let questionId = '';
    if (freeTextArea) {
      freeText = freeTextArea.value;
    }

    if (choicesContainer) {
      let choice = choicesContainer.querySelector('a[class~="active"]');
      questionId = choice.dataset['fitQuestionId'];
    }

    post('/course/survey/submit',
        {segment_id: t.dataset['fitSegmentId'],
          free_text: freeText,
          question_id: questionId
        },
        (responseText, xhr) => {
        if (xhr.status === 200) {
          showAlertSnackbar("Thank you for submitting answer");
          nextSegment(true)
        } else {
          showAlertSnackbar(JSON.parse(xhr.response)['message'])
        }});
  });

  delegate('[data-fit-skip-segment]', 'click', (e, t) => {
    nextSegment(true)
  });

  // and set it automatically from the slug name
  delegate("[data-fit-slug-name]", "keyup",
      (e, t) => {
      // if it's empty, unset user input
      if (slug_pretty === ''){
        slug_userset = false;
      }

      // only if user hasn't set it manually:
      if (slug_userset === false){
        // first bit
        let slugFirstElement = t.closest('form').querySelector('[data-fit-slug-first]');
        if (slugFirstElement && slugFirstElement.value !== ''){
          slug_ugly = slugFirstElement.value;
        }

        // add second if there
        let slugLastElement = t.closest('form').querySelector('[data-fit-slug-last]');
        if (slugLastElement && slugLastElement.value !== ''){
          slug_ugly = (slug_ugly + slugLastElement.value);
        }
      }

      fit_slug_set();
  });

});
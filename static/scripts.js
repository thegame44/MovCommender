$(document).ready(function(){
    $("button").click(function(){
        var className = $("#test").attr("class");
        if(className=='fa-solid fa-chevron-down'){
          $("#test").removeClass('fa-solid fa-chevron-down').addClass('fa-solid fa-chevron-up');
        }
        else{
          $("#test").removeClass('fa-solid fa-chevron-up').addClass('fa-solid fa-chevron-down');
        }
    });
});


var choices = ['','','','','','','','','',''];
var got_alr = 0;


function disable_submit_buttons(e) {
  $(e).html(`<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...`); 
  $(e).css("pointer-events", "none");
  $(e).css("background", "#2a9ed8");
};

function disable_search_buttons() {
  $('#search_button').html(`<div class="spinner-border text-primary" role="status" style="margin-top: 15px; width: 25px;height:25px;">
  <span class="visually-hidden">Loading...</span></div>`); 
  $('#search_button').css("pointer-events", "none");
};



function myFunction() {
  // var computedFontSize = window.getComputedStyle(document.getElementById("FirstTitle")).fontSize;
  var newWidth = window.innerWidth;
  var newHeight = window.innerHeight; 

  try {
    if ( newWidth <= 900){
      document.getElementById("FirstTitle").style.fontSize = 45 + "px"
    }
    else {
      document.getElementById("FirstTitle").style.fontSize = 5 + "vw"
    }
  
    if ( newWidth <= 600){
      document.getElementById("SecondTitle").style.fontSize = 1.4 + 'em'
    }
    else {
      document.getElementById("SecondTitle").style.fontSize = 1.7 + 'em'
    }
  }
  catch {
    // pass
  }

  try {
    if ( newWidth <= 444){
      document.getElementById("footerr").style.fontSize = .8 + 'em'
    }
    else {
      document.getElementById("footerr").style.fontSize = .9 + 'em'
    }
  }
  catch {
    // pass
  }

  try {
    if ( newWidth <= 550){
      document.getElementById("q-4-radio-buttons").style.width = 100 + '%' 
    }
    else {
      document.getElementById("q-4-radio-buttons").style.width = 40 + '%' 
    }
  }
  catch {
    // pass
  }

  try {
    if ( newWidth <= 940){
      document.getElementById("result").style.width = 100 + '%' 
      document.getElementById("get_another_rec").style.marginTop = 5 + 'px';
      document.getElementById("rec_footer").style.position = 'relative';
    }
    else {
      document.getElementById("result").style.width = 870 + 'px' 
      document.getElementById("get_another_rec").style.marginTop = 0 + 'px';
      document.getElementById("rec_footer").style.position = 'absolute';
    }
  }
  catch {
    // pass
  }
  
//   console.log(computedFontSize);
}
window.onresize = myFunction;
window.onload = myFunction;



$(document).on('click','.question-buttons',function(e) {
  try
  {
    let myAnchor = document.getElementById("question"); 
    var quest = myAnchor.getAttribute("target");
  }
  catch 
  {
    // Error - page not found
  };
  q_n = quest.replace(/[A-Za-z$-]/g, "");
  try {
    if (quest != 'question1') {
      if (quest != 'result') {
        choices[q_n - 2] = document.querySelector("input[type='radio'][name=radio]:checked").value;
      }
      else {
          choices[6] = document.querySelector("input[type='radio'][name=radio]:checked").value;
          choices[7] = document.querySelector("input[type='radio'][name=radio1]:checked").value;
          choices[8] = document.querySelector("input[type='radio'][name=radio2]:checked").value;
          choices[9] = document.querySelector("input[type='radio'][name=radio3]:checked").value;
      }
    };
  }
  catch {
    try {
      var markedCheckbox = document.querySelectorAll('input[type="checkbox"][name=radio]:checked');  
      var checkedval = [];
      checkedval.push('|');   
      for (var checkbox of markedCheckbox) {  
        checkedval.push(checkbox.value);   
        choices[q_n - 2] = checkedval;  
      } 
      checkedval.push('|');   
    }
    catch {
      console.log("Something went wrong! try refreshing the page.")
    };
  };
  if (quest != 'result') {
    $.ajax({
      url: "/"+ quest,
      type: "get",
      // data: {jsdata: 'hi there'},
      success: function(response) {
        const string = response;

        if (string.indexOf('<div class="main-container">') !== -1){
          $("#infodiv").html(response);
        }
        else {
          document.write(response);
        }
      },
      error: function(xhr) {
        //Do Something to handle error
      }
    });
  }
  
  if (quest == 'result') {
      String.prototype.format = function (args) {
        var newStr = this;
        for (var key in args) {
            newStr = newStr.replace('{' + key + '}', args[key]);
        }
        return newStr;
      }
      $.get( "/getmethod/{i}".format({ i: choices }));
      $.ajax({
        url: "/target_endpoint",
        type: "get",
        // data: {jsdata: 'hi there'},
        success: function(response) {
          const string = response;

          if (string.indexOf('<div class="main-container">') !== -1){
            $("#infodiv").html(response);
          }
          else {
            document.write(response);
          }
        },
        error: function(xhr) {
          //Do Something to handle error
        }
      });
    } 
});


$(document).on('click','.back-buttons',function(e) {
    String.prototype.format = function (args) {
      var newStr = this;
      for (var key in args) {
          newStr = newStr.replace('{' + key + '}', args[key]);
      }
      return newStr;
    };

    try
    {
      let myAnchor = document.getElementById("back-buttons"); 
      var quest = myAnchor.getAttribute("target");
    }
    catch 
    {
    };

    let q_n = quest.replace(/[A-Za-z$-]/g, "");

    try {
      if (quest != 'question6') {
        choices[q_n] = document.querySelector("input[type='radio'][name=radio]:checked").value;
      }
      else {

        choices[6] = document.querySelector("input[type='radio'][name=radio]:checked").value;
        choices[7] = document.querySelector("input[type='radio'][name=radio1]:checked").value;
        choices[8] = document.querySelector("input[type='radio'][name=radio2]:checked").value;
        choices[9] = document.querySelector("input[type='radio'][name=radio3]:checked").value;
      }
    }
    catch {
      try {
        var markedCheckbox = document.querySelectorAll('input[type="checkbox"][name=radio]:checked');
        var checkedval = [];
        for (checkbox of markedCheckbox) {
          checkedval.push(checkbox.value);
          choices[q_n] = checkedval;
        }
      }
      catch {
        console.log("Something went wrong! try refreshing the page.")
      };
    };

    $.ajax({
      url: "/"+ quest,
      type: "get",
      success: function(response) {
        const string = response;

        if (string.indexOf('<div class="main-container">') !== -1){
          $("#infodiv").html(response);
        }
        else {
          document.write(response);
        }
      },
      error: function(xhr) {
        //Do Something to handle error
      }
    });

});

try {
  const selectAll = document.querySelector('.form-group.select-all input');
  const allCheckbox = document.querySelectorAll('.form-group:not(.select-all) input');
  let listBoolean = [];
  
  allCheckbox.forEach(item=> {
    item.addEventListener('change', function () {
      allCheckbox.forEach(i=> {
        listBoolean.push(i.checked);
      })
      if(listBoolean.includes(false)) {
        selectAll.checked = false;
      } else {
        selectAll.checked = true;
      }
      listBoolean = []
    })
  })
  
  
  selectAll.addEventListener('change', function () {
    if(this.checked) {
      allCheckbox.forEach(i=> {
        i.checked = true;
      })
    } else {
      allCheckbox.forEach(i=> {
        i.checked = false;
      })
    }
  })
}
catch {
  //pass
}


function Chooseforme(){
  var checkboxs = document.querySelectorAll('input[type="checkbox"]');
  for (var checkbox of checkboxs) {
    checkbox.checked = this.unchecked;
  }
  document.getElementById('Not sure').checked = 'checked';
}

function stickyheaddsadaer(obj, id) {
  if($(obj).is(":checked")){
    document.getElementById('Not sure').checked = '';
    document.getElementById(obj.id).checked = 'checked';
  }
  var checked_boxs = [];
  var checkboxs = document.querySelectorAll('input[type="checkbox"]');
  for (var checkbox of checkboxs) {
    checked_boxs.push(checkbox.checked);
  }
  if (checked_boxs.indexOf(true) == -1){
    document.getElementById(obj.id).checked = 'checked';
  }
}








try {
  var selected = document.querySelector(".selected");
  var optionsContainer = document.querySelector(".options-container");
  var searchBox = document.querySelector(".search-box input");

  var optionsList = document.querySelectorAll(".option_t");
  var filterList = searchTerm => {
  searchTerm = searchTerm.toLowerCase();
  optionsList.forEach(option => {
    let label = option.firstElementChild.nextElementSibling.innerText.toLowerCase();
    if (label.indexOf(searchTerm) != -1) {
      option.style.display = "block";
    } else {
      option.style.display = "none";
    }
  });
};
}
catch {
  console.log('')
};

try {
  selected.addEventListener("click", () => {
    optionsContainer.classList.toggle("active");
  
    searchBox.value = "";
    filterList("");
  
    if (optionsContainer.classList.contains("active")) {
      searchBox.focus();
    }
  });
  
  optionsList.forEach(o => {
    o.addEventListener("click", () => {
      selected.innerHTML = o.querySelector("label").innerHTML;
      optionsContainer.classList.remove("active");
    });
  });
  
  searchBox.addEventListener("keyup", function(e) {
    filterList(e.target.value);
  });
}
catch {
  //pass
}



$(document).ready(function()
{

// global
const $loading = $('<div class="meter"><span style="width: 100%"></span></div>');

// Editor specific wrapper functions

function getEditorDimensions()
{
    var $content = $('.mc-content');
    var width = $content.innerWidth();
    var height = $content.innerHeight();
    return [width, height];
}

// View checking

function getView()
{
    return $('.toolset.tool-choice .button.active').attr("rel");
}

function setCurrentSDF(sdf)
{
    var view = getView();
    if (view == "2d")
    {
        mol = chemdoodleSetMol(sketcher, sdf);
    }
    else
    {
        jsmolSetMol(myJmol1, sdf);
        jsmolCmd(myJmol1, "minimize addHydrogens");
    }
    return false;
}

function getCurrentSDF(includeHydrogen=false)
{
    var view = getView();
    var mol;

    if (view == "2d")
    {
        mol = chemdoodleGetMol(sketcher);
    }
    else
    {
        mol = jsmolGetMol(myJmol1, includeHydrogen=includeHydrogen);
    }

    return mol;
}


// Production ///////////////////////////////////////////////////



// Chemdoodle
$('.toolset.chemdoodle a.button.chemdoodle').click(function () {
    chemdoodleEditorBtn($(this));
    return false;
});

waitForElement("#sketcherSingle", function() {
    setTimeout(function() {
        chemdoodleResize(sketcher, getEditorDimensions()); // Resize
    }, 100);
});


// Jsmol
var $jsmolMinimizeBtn = $('.action.minimize .button');
$jsmolMinimizeBtn.click(function()
{
    jsmolCmd(myJmol1, 'minimize');
    return false;
});

var $jsmolMinimizeBtn = $('.action.undo .button');
$jsmolMinimizeBtn.click(function()
{
    jsmolCmd(myJmol1, 'undo');
    return false;
});

var $jsmolAtomBtns = $('.action.atom .button');
$jsmolAtomBtns.click(function ()
{

    var cmd = $(this).attr('rel');
    $('.toolset.jsmol .action.atom .button.active').removeClass("active");

    switch(cmd)
    {
        case 'off':
            jsmolCmd(myJmol1, 'set atomPicking off');
            break;
        case 'dra':

            jsmolCmd(myJmol1, 'set atomPicking on');
            jsmolCmd(myJmol1, 'set picking dragMinimize'); // on off
            $(this).addClass('active');
            break;
        default:
            jsmolCmd(myJmol1, 'set atomPicking on');
            jsmolCmd(myJmol1, 'set picking dragMinimize');
            jsmolCmd(myJmol1, 'set picking assignAtom_'+cmd);
            $(this).addClass('active');
    }

    return false;
});

$jsmolBondBtns = $('.toolset.jsmol .action.bond .button')
$jsmolBondBtns.click(function()
{
    var bond = $(this).attr('rel');
    $(".toolset.jsmol .action.bond .button.active").removeClass('active');

    if(bond == 'n')
    {
        jsmolCmd(myJmol1, 'set bondpicking false;');
    }
    else
    {
        jsmolCmd(myJmol1, 'set picking assignBond_'+bond+';');
        $(this).addClass('active');
    }

    return false;
});


// Resize editors on window resize
function onWindowResize()
{
    $(window).on('resize', function()
    {
        chemdoodleResize(sketcher, getEditorDimensions());
    });
}

// Refresh before play
onWindowResize();


// Switch between 3D and 2D
// $('#editor-jsmol').hide();
// $('.toolset.jsmol').hide();
$('#editor-chemdoodle').hide();
$('.toolset.chemdoodle').hide();

swithBtns = $('.toolset.tool-choice .button').click(function () {

    $that = $(this);

    if($that.hasClass("active"))
    {
        return false;
    }

    var cont = $that.attr("rel");

    if(cont == "3d")
    {
        var sdf = chemdoodleGetMol(sketcher);

        jsmolSetMol(myJmol1, sdf);
        jsmolCmd(myJmol1, "minimize addHydrogens");

        $('#editor-chemdoodle').hide();
        $('.toolset.chemdoodle').hide();
        $('#editor-jsmol').show();
        $('.toolset.jsmol').show();
    }
    else if (cont == "2d")
    {
        var sdf = jsmolGetMol(myJmol1);

        chemdoodleSetMol(sketcher, sdf);
        chemdoodleResize(sketcher, getEditorDimensions());

        $('#editor-jsmol').hide();
        $('.toolset.jsmol').hide();
        $('#editor-chemdoodle').show();
        $('.toolset.chemdoodle').show();
    }

    swithBtns.removeClass("active");
    $that.addClass("active");

    return false;

});

// Load molecules
$('.toolset .load_benzene').click(function () {

    setCurrentSDF(sdfBenzene);
    return false;
});
// $('.toolset .load_methane').click(function () {
//
//     // Structure defined in html template
//     setCurrentSDF(sdfMethane);
//     return false;
// });
$('.toolset .load_water').click(function () {

    setCurrentSDF(sdfWater);
    return false;
});
// $('.toolset .load_carbon_dioxide').click(function () {
//
//     setCurrentSDF(sdfCarbonDioxide);
//     return false;
// });
// $('.toolset .load_ozone').click(function () {
//
//     setCurrentSDF(sdfOzone);
//     return false;
// });
// $('.toolset .load_nitrous_oxide').click(function () {
//
//     setCurrentSDF(sdfNitrousOxide);
//     return false;
// });

///////////////////////////////////////////////////////////////////////////////
// Select theory level for quantum chemistry
///////////////////////////////////////////////////////////////////////////////
function getTheoryLevel() {
    var lvl = $('.toolset.quantum .button.theory.active').attr('rel');
    return lvl;
}

//-----------------------------------------------------------------------------
//var theoryBtns = $('.toolset.quantum .button.theory');
$('.button.theory').click(function() {

    if( $(this).hasClass('active') ) {
        return false;
    }

    $('.toolset.quantum .button.theory.active').removeClass('active');
    $(this).addClass('active');

    return false;
});



///////////////////////////////////////////////////////////////////////////////
// Get IUPAC name for current structure
///////////////////////////////////////////////////////////////////////////////
function getIUPACName() {
    var lvl = $('.toolset.quantum .button.theory.active').attr('rel');
    return lvl;
}


///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
var IUPACName;
function callback(response) {
    IUPACName = response.toLowerCase();
}

// Get name
$('.button.getName').click(function () {

    // Setup loading
    var $loading = $('<div class="meter"><span style="width: 100%"></span></div>');
    var promptWait = new $.Prompt();
    promptWait.setMessage($loading);
    promptWait.setType("transparent");
    promptWait.show();

    // prepare smiles
    var mol = getCurrentSDF();
    var search = sdfToSmiles(mol);

    requestCactus(search, 'iupac_name', function(data) {
            IUPACName = data.toLowerCase();
            // callback(data);

            var promptCactus = new $.Prompt();
            promptCactus.setMessage(IUPACName);
            promptCactus.addCancelBtn("OK");
            promptCactus.show();
            promptWait.cancel();
        }, function(status)
        {
            promptWait.cancel();
        }
    );

    return false;
});


// Move to quantum
$('.button.quantum').click(function () {

    var promptQuantum = new $.Prompt();
    promptQuantum.setMessage('Ready to calculate <strong>quantum chemical properties</strong> for the molecule?');
    promptQuantum.addResponseBtn('Let\'s Go!', function()
    {
        var $loading = $('<div class="meter"><span style="width: 100%"></span></div>');
        var promptCalculation = new $.Prompt();
        promptCalculation.setMessage($loading);
        promptCalculation.setType("transparent");
        promptCalculation.show();
        promptQuantum.cancel();

        var mol = getCurrentSDF(include_hydrogen=true);
        var currentView = getView();
        var addHydrogens = 1
        if (ciEquals(currentView, "3d")){
            addHydrogens = 0
        }
        var theoryLevel = getTheoryLevel();

        var sdf_data = {
            sdf: mol,
            add_hydrogens: addHydrogens,
            current_view: currentView,
            theory_level: theoryLevel,
            iupac_name: IUPACName,
            trivial_name: "trivial_name"
        };

        request("/ajax/_submit_quantum", sdf_data, function (data)
        {
            let url = window.location.href;
            console.warn({url});
            url = url.split("#");
            url = url[0]
            url = url.replace('editor', '');
            url = url + 'calculations/' + data["hashkey"];
            window.location = url;
            promptCalculation.cancel();
        }, function() {
            promptCalculation.cancel();
        }, timeout=60000);
    });
    promptQuantum.addCancelBtn("Not yet");
    promptQuantum.show();

    return false;
});



// // Searchbar
var $searchFrm = $(".mc-editor-searchbar form");
var $searchBar = $(".mc-editor-searchbar");
var $searchBtn = $(".mc-editor-searchbar a");
var $searchInp = $(".mc-editor-searchbar input");
var $searchBarCloseBtn = $(".mc-editor-searchbar .searchbar-close");
var $searchBarBtn = $(".mc-mobile-search a");


function changeInputStatus(input, stats) {

    input.removeClass();
    input.addClass(stats);

    if(stats == "loading") {
        input.prop('disabled', true);
    }
    else{
        input.prop('disabled', false);
    }

}

$searchInp.on('blur', function() {

    $searchBar.removeClass("active");

});

$searchInp.on('focus', function() {

});

$searchBarBtn.click(function () {

    $searchBar.addClass("active");

    setTimeout(function() {
        $searchBar.find("input:first").focus();
        return false;
    }, 100);


    return false;

});

$searchBarCloseBtn.click(function() {
    $('.mc-header').focus();
    return false;
});

$searchFrm.submit(function(event) {

    event.preventDefault();

    changeInputStatus($searchInp, "loading");

    var promptWait = new $.Prompt();
    promptWait.setMessage($loading);
    promptWait.setType("transparent");
    promptWait.show();

    var search = $searchInp.val();

    if (!search || 0 === search.length)
    {
        changeInputStatus($searchInp, "empty");
        $searchInp.focus();
        return false;
    }

    requestCactus(search, 'smiles', function(data)
    {
        var promptSearch = new $.Prompt();
        promptSearch.setMessage("Converting " + data);
        promptSearch.show();

        // Convert to sdf
        var sdfstr = smilesToSdf(data);
        setCurrentSDF(sdfstr);

        promptSearch.cancel();
        onWindowResize();

        // reset search on success
        $searchInp.focus();
        // $searchInp.val(""); // Casper didn't like this behavior
        changeInputStatus($searchInp, 'success');
        promptWait.cancel();

    }, function(status)
    {
        changeInputStatus($searchInp, 'failed');
        promptWait.cancel();
    });

    return false;
});


// End
});
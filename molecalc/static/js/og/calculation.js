$(document).ready(function() {

// View the current 'tab'

firstHash = getHash();

$menu = $('.mc-content .calc-menu');
$menu_items = $('.mc-content .calc-menu a');
$sections = $('.mc-content');

if(firstHash != "") {
    $menu.find('a').removeClass('active');
    $menu.find('a.'+firstHash).addClass('active');

    $sections.find(".calc").removeClass('active');
    $sections.find('.calc.tab-'+firstHash).addClass('active');
}


var $sidebars = $('.sidebar');

// ******************************************************************
$('.calc-menu ul a').each(function () {
    var active = "active";
    var that = $(this);
    var type = that.attr('class');
    type = type.replace(" active", "");
    var content = $('.calc.tab-'+type);

    that.click(function()
    {
        if(that.hasClass(active)) return false;

        $menu_items.removeClass(active);
        that.addClass(active);
        $sections.find('.calc').removeClass(active);
        $sections.find(".calc.tab-"+type).addClass(active);

        setHash(type);

        $sidebars.removeClass("active");

        return false;
    });
});


// Jsmol
// var $jsmolMinimizeBtn = $('.action.minimize .button');
// $jsmolMinimizeBtn.on('click', function() {
//     jsmolCmd(myJmol1, 'refresh');
//     return false;
// });


}); // End


function jsmolSetBGColor(jmolObj, color) {
    Jmol.script(jmolObj, 'set backgroundColor "' + color + '"');
}

function jsmolSetFontColor(jmolObj, color) {
    Jmol.script(jmolObj, 'color echo "' + color + '";');
}

function  getModeFontColor() {
    if (isDarkMode()) {
        return '#FFFFFF';
    } else {
        return '#000000';
    }
}

function jsmolDisplayText(jmolObj,
                          text,
                          loc,
                          fontsize= 16,
                          fontstyle = 'sanserif') {
    let font_color = getModeFontColor();
    jsmolSetFontColor(jmolObj, font_color);  // Set the font color based on light/dark mode
    Jmol.script(jmolObj, 'font echo ' + fontsize + ' ' + fontstyle + ';');
    Jmol.script(jmolObj, 'set echo ' + loc + ';');
    Jmol.script(jmolObj, 'echo "' + text + '";');
}

// Specific to the solvation calculation section
function setSolvationText(jmolObj) {
    let font_color = getModeFontColor();
    console.log("The font color is " + font_color)
    Jmol.script(jmolObj, 'color echo "' + font_color + '"; font echo 13; echo Blue: Positive, Red: Negative;');
    Jmol.script(jmolObj, 'color echo "' + font_color + '"; font echo 13; echo Mouse over atoms for partial charge;');
}


var gulp = require("gulp");
var less = require("gulp-less");
var concat = require("gulp-concat");
var uglify = require("gulp-uglify");
var plumber = require("gulp-plumber");
var minifycss = require("gulp-cssnano");
var through = require('through2');
var parseArgs = require('minimist');
var env = parseArgs(process.argv.slice(2));
var PRODUCTION = env.production || process.env.NODE_ENV == "production";

var STATIC_SRC_PATH = "asylum/static_src/";
var STATIC_DEST_PATH = "asylum/static/";
var BOWER_PATH = "bower_components/"

function noop () {
  return through.obj();
};

function task_less() {
    return gulp.src([
        STATIC_SRC_PATH + "less/style.less"
    ])
        .pipe(plumber({}))
        .pipe(less().on("error", function(err) {
            console.log(err.message);
            this.emit("end");
        }))
        .pipe(concat("asylum.css"))
        .pipe((PRODUCTION ? minifycss() : noop()))
        .pipe(gulp.dest(STATIC_DEST_PATH + "css/"));
}

task_less.displayName = "less"

function watch_less(cb) {
    gulp.watch([STATIC_SRC_PATH + "less/**/*.less"], gulp.series(task_less));
}

function task_js() {
    return gulp.src([
        BOWER_PATH + "jquery/dist/jquery.min.js",
        BOWER_PATH + "bootstrap/dist/js/bootstrap.min.js",
        STATIC_SRC_PATH + "js/asylum.js",
    ])
        .pipe(plumber({}))
        .pipe(concat("asylum.js"))
        .pipe((PRODUCTION ? uglify() : noop()))
        .pipe(gulp.dest(STATIC_DEST_PATH + "js/"));
}

task_js.displayName = "js"

function task_copy_fonts() {
    return gulp.src([
        BOWER_PATH + "font-awesome/fonts/*"
    ]).pipe(gulp.dest(STATIC_DEST_PATH + "fonts/"));
}

task_copy_fonts.displayName = "copy_fonts"

function watch_js(cb) {
    gulp.watch([STATIC_SRC_PATH + "js/**/*.js"], gulp.series(task_js));
}

exports.default = gulp.series(task_js, task_less, task_copy_fonts);

exports.watch =  gulp.series(watch_js, watch_less);

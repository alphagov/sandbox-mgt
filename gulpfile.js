'use strict';

var gulp = require('gulp');
var sass = require('gulp-sass');
var concat = require('gulp-concat');
var watch = require('gulp-watch');
var batch = require('gulp-batch');


var repo_root = __dirname + '/';
var govuk_frontend_toolkit_root =
  repo_root + 'node_modules/govuk_frontend_toolkit/stylesheets'; // 1.
var govuk_elements_sass_root =
  repo_root + 'node_modules/govuk-elements-sass/public/sass';       // 2.

var assets = './src/assets';

var ignoredFiles =
  [ '.*', '#*', 'app_flymake.js' ]
    .map(function(p) { return '!'+assets+'/**/'+p; });

// Compile scss files to css

var scssFiles = ignoredFiles.concat(
  [ assets + '/scss/*.scss'
  ]);

gulp.task('styles', function () {
  return gulp.src(scssFiles)
    .pipe(sass({includePaths: [
      govuk_frontend_toolkit_root,
      govuk_elements_sass_root
      ]}).on('error', sass.logError))
    .pipe(gulp.dest(assets + '/css'));
});

//script paths
var jsFiles = ignoredFiles.concat(
  [ assets + '/javascripts/vendor/jquery/*.js'
  , assets + '/javascripts/vendor/polyfills/*.js'
  , assets + '/javascripts/govuk/**/*.js'
  , assets + '/javascripts/vendor/typeahead.bundle.min.js'
  , assets + '/javascripts/*.js'
  ]);

var jsDest = assets + '/js';

gulp.task('scripts', function() {
    return gulp.src(jsFiles)
        .pipe(concat('main.js'))
        .pipe(gulp.dest(jsDest));
});

gulp.task('watchScripts', function () {
  watch(
    jsFiles,
    { ignoreInitial: false },
    batch(function (events, done) {
      gulp.start('scripts', done);
    })
  );
});

gulp.task('watchStyles', function () {
  watch(
    scssFiles,
    { ignoreInitial: false },
    batch(function (events, done) {
      gulp.start('styles', done);
    })
  );
});

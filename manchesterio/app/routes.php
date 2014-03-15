<?php

Route::get('/{path?}', 'ManchesterIo\DefaultController@defaultAction')->where('path', '/.+');

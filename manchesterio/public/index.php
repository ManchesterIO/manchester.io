<?php

require_once __DIR__.'/../vendor/autoload.php';

$app = new Silex\Application();

$app['debug'] = true;
$app['backend-url'] = 'http://localhost:8000';

$app['backend-http-client'] = function ($app) {
    $client = new GuzzleHttp\Client([
        'base_url' => $app['backend-url'],
        'defaults' => [
            'headers' => [
                'Accept' => 'application/json'
            ]
        ]
    ]);
    return $client;
};

$app->register(new Silex\Provider\TwigServiceProvider(), array(
    'twig.path' => __DIR__ . '/../views',
    'twig.options' => [
        'cache' => __DIR__ . '/../views/template_cache',
        'strict_variables' => true
    ]
));

$app['controller-http://mollyproject.org/apps/homepage'] = function ($app) {
    return new ManchesterIo\HomePage($app['twig']);
};

$app->get(
    '/{path}',
    function (Silex\Application $app, Symfony\Component\HttpFoundation\Request $request, $path) {
        try {
            $response = $app['backend-http-client']->get($path, ['query' => $request->query->all()])->json();
        } catch (GuzzleHttp\Exception\RequestException $ex) {
            if ($ex->hasResponse()) {
                $app->abort($ex->getResponse()->getStatusCode());
            } else {
                $app->abort(500, 'Backend response failed');
            }
        }
        $silexControllerName = 'controller-' . $response['self'];
        if (isset($app[$silexControllerName])) {
            return $app[$silexControllerName]->render($response);
        } else {
            $app->abort(404);
        }
    }
)->assert('path', '.*');

$app->run();

---
title: Designing a RESTful Web API
layout: wikistyle
---

# Designing a RESTful Web API

Author: Luis Rei
<me@luisrei.com>
[@lmrei](http://twitter.com/lmrei)
[http://luisrei.com](http://luisrei.com)

Date: 26 February 2012
 

## Purpose, Scope, Miscellaneous
I decided to write this article to serve as my personal "*quick start guide*" for designing RESTful Web APIs. As such, this document is concerned with the *how* rather than the *why*. For the latter, check the Bibliography.


## Everything is a Resource
Any interaction of a RESTful API is an interaction with a resource. In fact, the API can be considered simply as mapping and endpoint - or, **resource identifier** (URL) - to a resource. Resources are sources of information, typically documents or services. A user can be thought of as resource and thus has an URL such as in the case of [GitHub][ghv3]:

	https://api.github.com/users/lrei

Resources can have different **representations**. The above mentioned user has the following JSON representation (partial document):

	{
	 	"login": "lrei",
    	"created_at": "2008-11-21T14:48:42Z",
    	"name": "Luis Rei",
    	"email": "me@luisrei.com",
    	"id": 35857,
    	"blog": "http://luisrei.com"
	}


## Actions: HTTP Verbs and Response Codes

**Resources are Nouns!** This fictional API URL:

	http://api.example.com/posts/delete/233/

is wrong. It's obvious that *delete* is an action, not a resource. The way to do perform an action in a RESTful web service is to use HTTP **verbs** or **request methods**:

<table>
<tbody><tr><th>HTTP Verb</th>
<th>Action (typical usage)</th>
</tr>
<tr>
<td>GET</td>
<td>retrieves a representation of a resource without side-effects (nothing changes on the server).</td>
</tr>
<td>HEAD</td>
<td>retrieves just the resource meta-information (headers) i.e. same as GET but without the response body - also without side-effects.</td>
</tr>
<tr>
<td>OPTIONS</td>
<td>returns the actions supported for specified the resource - also without side-effects.</td>
</tr>
<tr>
<td>POST</td>
<td>creates a resource.</td>
</tr>
<tr>
<td>PUT</td>
<td>(completely) replaces an existing resource.</td>
</tr>
<tr>
<td>PATCH</td>
<td>partial modification of a resource.</td>
</tr>
<tr>
<td>DELETE</td>
<td>deletes a resource.</td>
</tr>

</tbody></table>

When using PUT, POST or PATCH, send the data as a document in the body of the request. Don't use query parameters to alter state. An example from the [GitHub API][ghv3]:

	POST https://api.github.com/gists/gists
	{
		"description": "the description for this gist",
		"public": true,
		"files": {
			"file1.txt": {
			"content": "String file contents"
			}
		}
		...
	}

There's also a proper way to do **responses**: using the [HTTP Response Codes and Reason Phrase][httpresponse]. The reply to the previous request includes the following header:

	201 Created
	Location: https://api.github.com/gists/1

If one were to make the following request afterwards:

	GET https://api.github.com/gists/1

The expected reply status code would be:

	200 OK

A RESTful HTTP server application has to return the status code according to the HTTP specification. Returning the created resource in the POST requests' response body is optional, the location of the created resource is not.

## For Everything Else, There Are Headers
Resources are mapped to URLs, actions are mapped to verbs and the rest goes in the headers.

### Content Negotiation and Versioning
Choosing between different representations of the same resource is a matter of using [HTTP content negotiation][httpcontent]:

	GET https://api.github.com/gists/1
	Accept: application/json
to get the JSON representation of a resource and

	GET https://api.github.com/gists/1
	Accept: application/xml
to get the XML representation of the same resource. The responses  for this example requests were:

	200 OK
	Content-Type: application/json; charset=utf-8
	(response body)
because the resource was available in JSON

	406 Not Acceptable
	Content-Type: application/json
	{
    "message": "Must ACCEPT application/json: [\"application/xml\"]"
	}

because GitHub gists are (currently) not available in XML representation. Notice that the 406 response body can be in whatever representation the server chooses, in this case it was JSON even though the client had requested something else (e.g. XML).

More broadly speaking, representation isn't just about file format, it could also be used for compression or to select between different languages:

	GET /resource
	Accept-Language: en-US
	Accept-Charset: iso-8859-5
	Accept-Encoding: gzip

There's one more big thing that the Accept header can handle for RESTful Web APIs: **versioning**. Here's an example (from [spire.io][spire]) that includes both the resource representation and the version of the API being used:

	Accept: application/vnd.spire-io.session+json;version=1.0


### Caching
There are two main HTTP response headers for controlling caching behavior: **Expires** which specifies an absolute expiry time for a cached representation and **Cache-Control** which specifies a relative expiry time using the *max-age* directive.

Both work in combination with **ETag** (entity tag) which is an identifier, commonly a hash, that changes when the resource changes thereby invalidating cached versions or a **Last-Modified** header which is just the last modified date of the resource.

The request:

	GET https://api.github.com/gists/1
	Accept: application/json
*had* the reply:

	200 OK
	ETag: "2259b5bea67655550030acf98bad4184"
	

and a later request using

	GET https://api.github.com/gists/1
	Accept: application/json
	If-None-Match: "2259b5bea67655550030acf98bad4184"
will return

	304 Not Modified
without a response body. The same could be accomplished using Last-Modified/If-Modified-Since headers.


### Authorization
Trying to create a repo on GitHub:

	POST https://api.github.com/user/repos
and the reply:

	401 Unauthorized
	WWW-Authenticate: Basic realm="GitHub"

which means that making a POST request to /user/repos requires basic HTTP authentication which uses the Authorization header with the base64 encoded string "*username*:*password*":

	POST https://api.github.com/user/repos
	Authorization: Basic bHJlaTp5ZWFocmlnaHQ=

Basic HTTP authentication should always be used in combination with SSL/TLS (HTTPS) since otherwise the username/password will be susceptible to interception.

[OAuth2](http://oauth.net/2/) is a common way of doing authorization for 3rd party applications using an API but beyond the scope of this document.

### Rate Limiting
HTTP does not currently have any standard for rate limiting. GitHub uses:

	GET https://api.github.com/gists/1
or any other request which results in the response headers:

	200 OK
	X-RateLimit-Limit: 5000
	X-RateLimit-Remaining: 4966

This indicates that the client is limited to making 5000 API requests/hour and that the client can make 4966 requests during the next hour. By convention, non-standard headers are prefixed with *X-*.

The most widely known implementation of rate limiting is probably [twitter's](https://dev.twitter.com/docs/rate-limiting). It is similar to GitHub's but also includes a *X-RateLimit-Reset* which indicates when the limits will be reset. A particular API call or set of API calls may also be subject to additional limits. Twitter implements these with *X-FeatureRateLimit-Limit*, *X-FeatureRateLimit-Remaining* and *X-FeatureRateLimit-Reset*.

When denying a request based on rate limiting, the status code should be 403 Forbidden accompanied by by a message explaining the reason for the rejection.

## HATEOAS, OPTIONS and Error Handling

> A REST API **must not** define fixed resource names or hierarchies (an obvious coupling of client and server). Servers **must have** the freedom to control their own namespace (…) Failure here implies that clients are assuming a resource structure due to out-of-band information (…) A REST API **should** be entered with no prior knowledge beyond the initial URI. - [Roy Thomas Fielding][hypertext] (my emphasis)

In other words, in a truly REST based architecture any URL, except the initial URL, can be changed, **even to other servers**, without worrying about the client.

Hypermedia As The Engine Of Application State, HATEOAS, can be reduced to thinking of the API as a state machine where resources are thought of as states and the transitions between states are links between resources and are included in their representation (hypermedia).

The first state is obviously the root URL. So let's start with the root of Spire.io's API:

	GET https://api.spire.io
results in:

	200 OK
	{
	    "url": "https://api.spire.io/",
	    "resources": {
	        "sessions": {
	            "url": "https://api.spire.io/sessions"
	        },
	        "accounts": {
	            "url": "https://api.spire.io/accounts"
	        },
	        "billing": {
	            "url": "https://api.spire.io/billing"
	        }
	    }
	…

The root resource, or *initial state*, contains the transitions to the other resources (or states) reachable from it: "sessions", "accounts" and "billing".

It's also possible to include the transitions in the HTTP response Link header, for example:

	GET /gists/starred
can result in the following response:

	200 OK
	Link: <https://api.github.com/resource?page=2>; rel="next",
      <https://api.github.com/resource?page=5>; rel="last"


In the case of non-hypermedia resources (e.g. images) the http headers will be the only way to add API metadata to the resource such as state transitions. I think it's generally a good idea to always include the transitions in the headers as it becomes possible to perform a transition without parsing the request body.

### Options
Another useful bit of information is what actions can be performed on a given resource. The way to find that out is to use the HTTP request method OPTIONS:

	OPTIONS https://api.spire.io/accounts
and the response:

	Status Code: 200
	access-control-allow-methods: GET,POST
	access-control-allow-origin: *

From the [HTTP/1.1 Method Definitions][httpmethods]:

> A 200 response [to an OPTIONS request] SHOULD include any header fields that indicate optional features implemented by the server and applicable to that resource (e.g., Allow), possibly including extensions not defined by this specification.

This seems like a good place to include information about  resource specific rate limits without the need to make a request that will count against such limits.

### Error Handling
An error response should consist of the following:

* The appropriate HTTP error status code and any other relevant headers;
* A human readable message in the appropriate format (including a link to the documentation);
* A *Link* header to a meaningful state transition if appropriate.

An example from the [twilio api][twilio]:

	GET https://api.twilio.com/2010-04-01/Accounts.json
results in:

	401 Unauthorized
	WWW-Authenticate: Basic realm="Twilio API"
	{
    	"status": 401,
    	"message": "Authenticate",
    	"code": 20003,
    	"more_info": "http:\/\/www.twilio.com\/docs\/errors\/20003"
	}


## Bibliography
[Architectural Styles and the Design of Network-based Software Architectures, Chapter 5: Representational State Transfer (REST)][field] - R. Fielding

[It is okay to use POST][postokay] - R. Fielding

[REST APIs must be hypertext-driven][hypertext] - R. Fielding

[Nobody Understands REST or HTTP](http://blog.steveklabnik.com/posts/2011-07-03-nobody-understands-rest-or-http) - Steve Klabnik

[field]: http://www.ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm "Roy Thomas Fielding: Architectural Styles and the Design of Network-based Software Architectures, Chapter 5: Representational State Transfer (REST)"

[postokay]: http://roy.gbiv.com/untangled/2009/it-is-okay-to-use-post

[Get some REST on twitter](http://twitter.com/getsomerestbook) - Steve Klabnik

[Versioning REST Web Services](http://barelyenough.org/blog/2008/05/versioning-rest-web-services/) - Peter Williams

[Hypertext Transfer Protocol -- HTTP/1.1 ](http://www.w3.org/Protocols/rfc2616/rfc2616) - R. Fielding, J. Gettys, J. Mogul, H. Frystyk, L. Masinter, P. Leach, T. Berners-Lee

[HTTP Authentication: Basic and Digest Access Authentication](http://tools.ietf.org/html/rfc2617) - J. Franks, P. Hallam-Baker, J. Hostetler, S. Lawrence, P. Leach, A. Luotonen, L. Stewart

[RESTful Error Handling](http://www.oreillynet.com/onlamp/blog/2003/12/restful_error_handling.html) - Ethan Cerami

[RESTful HTTP in practice][restfulpractice] - Gregor Roth

[How To GET a Cup of Coffee](http://www.infoq.com/articles/webber-rest-workflow) - Jim Webber, Savas Parastatidis, Ian Robinson

[REST in Practice](http://shop.oreilly.com/product/9780596805838.do) (Book) - Jim Webber, Savas Parastatidis, Ian Robinson

[RESTful Web Services](http://shop.oreilly.com/product/9780596529260.do) (Book) - Leonard Richardson, Sam Ruby

[RESTful Web Services Cookbook](http://shop.oreilly.com/product/9780596801694.do) (Book) - Subbu Allamaraju



[hypertext]: http://roy.gbiv.com/untangled/2008/rest-apis-must-be-hypertext-driven


[ghv3]: http://developer.GitHub.com/v3
[spire]: http://www.spire.io/docs/api/reference.html
[twilio]: http://www.twilio.com/docs/api/rest
[httpcontent]: http://www.w3.org/Protocols/rfc2616/rfc2616-sec12.html
[patch]: http://tools.ietf.org/html/rfc5789

[httpresponse]: http://www.w3.org/Protocols/rfc2616/rfc2616-sec6.html#sec6.1.1

[httpmethods]: http://www.w3.org/Protocols/rfc2616/rfc2616-sec9.html

[restfulpractice]: http://www.infoq.com/articles/designing-restful-http-apps-roth


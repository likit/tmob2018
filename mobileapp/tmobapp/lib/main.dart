import 'dart:async';
import 'dart:io';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_html_view/flutter_html_view.dart';
import 'package:flutter_webview_plugin/flutter_webview_plugin.dart';
import 'package:intl/intl.dart';
import 'facebook.dart' as fb;

String jwt_token;
bool isLoggedIn = false;
String profileCover;
int userId;
const host = '209.97.174.132';


final flutterWebViewPlugin = new FlutterWebviewPlugin();

void main() => runApp(new MainPage());

class Post {
  final String id;
  final String story;
  final String message;
  final String full_picture;
  final DateTime created_time;
  var postDateTime;

  Post(
      {this.id,
      this.story,
      this.message,
      this.full_picture,
      this.created_time});

  factory Post.fromJson(Map<String, dynamic> json) {
    Post post = Post(
      id: json['id'],
      story: json['story'],
      message: json['message'],
      full_picture: json['full_picture'],
      created_time: DateTime.parse(json['created_time']),
    );
    // this should be done another way that can make postDate final
    post.postDateTime =
        new DateFormat.yMMMd().add_jm().format(post.created_time);
    return post;
  }
}

class MainPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      initialRoute: '/',
      routes: {
        '/': (context) => PostsList(),
        '/login': (context) => FacebookLoginPage(),
        '/profile': (context)=>AccountPage(),
      },

      title: 'Talent Mobility App',
      theme: ThemeData(
        fontFamily: 'Prompt',
        brightness: Brightness.light,
        primaryColor: Colors.deepOrangeAccent,
        accentColor: Colors.blueGrey,
      ),
    );
  }
}

class PostsList extends StatefulWidget {
  createState() => new _PostsListState();
}

class _PostsListState extends State<PostsList> {
  List<Post> posts;

  List<Post> parsePosts(String responseBody) {
    // final parsed = json.decode(responseBody).cast<Map<String, dynamic>>();
    final parsed = json.decode(responseBody);
    print(parsed['data']);
    return parsed['data'].map<Post>((json) => Post.fromJson(json)).toList();
  }

  Future<Null> refreshPostList() async {
    setState(() {});
    return null;
  }

  final fb_access_key =
      'EAAEzlJsTZBB8BAFvEfLNZAQXzLV0V1YN3hWrOgW8VFZBCZBhelTWm9JphPEqkWvgjFustelwuLZBhNZAf67YmbW4kW80pYcUZCU5EwfzHT9JPuJhlv2cXEniP9w6NHMGx1XlmPAYTZAGcF8XZAHoDZB64yeeLcVPi1CTHiacerLhIPrAZDZD';

  Future<List<Post>> fetchPost() async {
    var response = await http.get(
        'https://graph.facebook.com/v2.9/241755426012824/posts?fields=id,message,story,full_picture,created_time&access_token=${fb_access_key}');
    // print(response.body);
    // final response = await http.get('http://209.97.174.132/api/v2/pages?type=blog.PostPage&fields=feed_image_thumbnail,body');
    if (response.statusCode == 200) {
      return posts = parsePosts(response.body);
    } else {
      throw Exception('Failed to load post');
    }
  }

  @override
  void initState() {
    super.initState();
    refreshPostList();
  }

  @override
  Widget build(BuildContext context) {
    FutureBuilder<List<Post>> postListFuture = FutureBuilder<List<Post>>(
        future: fetchPost(),
        builder: (context, snapshot) {
          if (snapshot.hasData) {
            return ListView.builder(
              itemCount: snapshot.data?.length,
              itemBuilder: (BuildContext context, index) {
                return Column(children: <Widget>[
                  Card(
                    elevation: 0.0,
                    child: Container(
                      padding: EdgeInsets.all(16.0),
                      child: Column(
                        children: <Widget>[
                          snapshot.data[index].full_picture != null
                              ? Image.network(
                                  '${snapshot.data[index].full_picture}')
                              : Container(),
                          Text('Shared on ${snapshot.data[index].postDateTime}', style: TextStyle(color: Colors.black45, fontSize: 12.0)),
                          snapshot.data[index].message != null ? Text('${snapshot.data[index].message}') : Text(''),
                          OutlineButton(
                            child: Text('อ่านรายละเอียดเพิ่มเติม...', style: TextStyle(fontSize: 12.0)),
                              shape: new RoundedRectangleBorder(borderRadius: new BorderRadius.circular(10.0)),
                              //elevation: 0.0,
                              borderSide: BorderSide(color: Colors.black38, width: 2.0),
                              highlightedBorderColor: Colors.white,
                              highlightColor: Colors.white,
                              onPressed: () {
                                //flutterWebViewPlugin.launch('https://facebook.com/${snapshot.data[index].id}');
                                Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                        builder: (context) => PreviewPost(
                                            postUrl:
                                            'https://facebook.com/${snapshot.data[index].id}')));
                              }
                          ),
                        ],
                      ),
                    ),
                  ),
                ]);
              },
            );
          } else {
            print(snapshot.error);
            return Center(child: CircularProgressIndicator());
          }
        });
    return new Scaffold(
      appBar: AppBar(
          elevation: 1.0,
          title: new Text('Recent Posts'),
          actions: <Widget>[
            new IconButton(
              icon: new Icon(Icons.account_circle),
              onPressed: () {
                Navigator.push(context,
                    MaterialPageRoute(builder: (context) => AccountPage()));
              },
            )
          ]),
      body: new RefreshIndicator(
        onRefresh: refreshPostList,
        child: postListFuture,
      ),
      bottomNavigationBar: BottomNavigationBar(items: [
        BottomNavigationBarItem(
          icon: Icon(Icons.category),
          title: Text('Posts'),
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.label),
          title: Text('Events'),
        ),
        BottomNavigationBarItem(
          icon: Icon(Icons.people),
          title: Text('Community'),
        )
      ]),
    );
  }
}

class PreviewPost extends StatelessWidget {
  final String postUrl;

  PreviewPost({Key key, @required this.postUrl}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return WebviewScaffold(
      url: postUrl,
      appBar: AppBar(
        elevation: 1.0,
        title: Text('Post Page'),
      ),
    );
  }
}

class DetailPost extends StatelessWidget {
  final Post post;

  DetailPost({Key, key, @required this.post}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        elevation: 1.0,
        title: Text('Post Page'),
      ),
      body: Container(
          margin: const EdgeInsets.all(16.0),
          child: SingleChildScrollView(
            child: Column(
              children: <Widget>[
                Text(
                  '${post.story}',
                  style: TextStyle(fontSize: 22.0),
                ),
                HtmlView(data: '${post.message}'),
              ],
            ),
          )),
      floatingActionButton: FloatingActionButton(
        child: Icon(Icons.format_quote),
        onPressed: () {
          Navigator.push(context,
              MaterialPageRoute(builder: (context) => PostCommentForm()));
        },
        tooltip: 'Show me the comment!',
      ),
    );
  }
}

class PostCommentForm extends StatefulWidget {
  @override
  _PostCommentFormState createState() => _PostCommentFormState();
}

class _PostCommentFormState extends State<PostCommentForm> {
  final commentInputCtrl = TextEditingController();
  @override
  void dispose() {
    commentInputCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        elevation: 1.0,
        title: Text('Post Comment'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: TextField(
          controller: commentInputCtrl,
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          return showDialog(
            context: context,
            builder: (context) {
              return AlertDialog(
                content: Text(commentInputCtrl.text),
              );
            },
          );
        },
        tooltip: 'Show me the comment!',
        child: Icon(Icons.text_fields),
      ),
    );
  }
}

class SearchPostForm extends StatefulWidget {
  @override
  _SearchPostFormState createState() => _SearchPostFormState();
}

class _SearchPostFormState extends State<SearchPostForm> {
  final inputCtrl = TextEditingController();
  @override
  void dispose() {
    inputCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        elevation: 1.0,
        title: Text('Search Post'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: TextField(
          controller: inputCtrl,
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          return showDialog(
            context: context,
            builder: (context) {
              return AlertDialog(
                content: Text(inputCtrl.text),
              );
            },
          );
        },
        child: Icon(Icons.text_fields),
      ),
    );
  }
}

class UserProfile {
  String name = '';
  String name_th = '';
  String currentAffiliation = '';
  String currentPosition = '';
  String contact = '';
  int id = null;

  UserProfile({this.id, this.name,
    this.name_th,
    this.currentAffiliation,
    this.currentPosition,
    this.contact});
  factory UserProfile.fromJson(Map<String, dynamic> json) {
    if (json['profile'] != null) {
      return UserProfile(
        id: json['id'],
        name: "${json['first_name']} ${json['last_name']}",
        name_th: "${json['profile']['first_name_th']} ${json['profile']['last_name_th']}",
        contact: json['email'],
        currentAffiliation: json['profile']['current_affiliation'],
        currentPosition: json['profile']['current_position'],
      );
    } else {
      return UserProfile(
        id: json['id'],
        name: "${json['first_name']} ${json['last_name']}",
        contact: json['email'],
        currentAffiliation: '',
        currentPosition: '',
      );
    }
  }
}


class AccountPage extends StatelessWidget {

  HttpClient httpClient = new HttpClient();

  Future<UserProfile> fetchProfile(int userId) async {
    var uri = Uri.http(host, '/account/api/users/${userId}');
    var request = await httpClient.getUrl(uri);
    var response = await request.close();
    var responseBody = await response.transform(UTF8.decoder).join();
    // final response = await http.get('http://209.97.174.132/api/v2/pages?type=blog.PostPage&fields=feed_image_thumbnail,body');
    if (response.statusCode == 200) {
      // setState(() {});
      return UserProfile.fromJson(json.decode(responseBody));
    } else {
      throw Exception('Failed to load post');
    }
  }

  @override
  Widget build(BuildContext context) {
    if(!isLoggedIn) {
      return Scaffold(
        appBar: AppBar(
          title: Text('Please log in'),
          elevation: 0.0,
        ),
        body: Center(
          child: Column(
            children: <Widget>[
              Expanded(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  mainAxisSize: MainAxisSize.min,
                  children: <Widget>[
                    IconButton(
                      icon: Icon(Icons.account_circle),
                      iconSize: 96.0,
                    ),
                    Container(
                      child: Text(
                        'Log in using your social account.',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 20.0),
                        textAlign: TextAlign.center,
                      ),
                      margin: const EdgeInsets.all(8.0),
                    ),
                    Container(
                      child: RaisedButton(
                        child: Text(
                            'Facebook account',
                            style: TextStyle(color: Colors.white)),
                        shape: RoundedRectangleBorder(borderRadius: new BorderRadius.circular(18.0)),
                        color: Colors.blue[500],
                        elevation: 0.0,
                        onPressed: () {
                          Navigator.pushNamed(context, '/login');
                        },
                      ),
                      margin: const EdgeInsets.all(8.0),
                    ),
                    Container(
                      child: RaisedButton(
                        child: Text(
                            'Google account',
                            style: TextStyle(color: Colors.white)),
                        shape: RoundedRectangleBorder(borderRadius: new BorderRadius.circular(18.0)),
                        color: Colors.deepOrangeAccent[400],
                        elevation: 0.0,
                        onPressed: () {},
                      ),
                      margin: const EdgeInsets.all(8.0),
                    ),
                  ],
                ),
              )
            ],
          ),
        ),
      );
    } else {
      return Scaffold(
        appBar: AppBar(
          title: Text('Profile'),
          elevation: 1.0,
        ),
        body: Container(
          padding: const EdgeInsets.all(16.0),
          child: Center(
            child: FutureBuilder<UserProfile>(
              future: fetchProfile(userId),
              builder: (context, snapshot){
                if(snapshot.hasData) {
                  return Column(
                    children: <Widget>[
                      CircleAvatar(
                        backgroundImage: NetworkImage(profileCover),
                        radius: 42.0,
                      ),
                      Text(''),
                      Text(
                        snapshot.data.name,
                        style: TextStyle(fontSize: 18.0,
                            fontWeight: FontWeight.bold),
                      ),
                      Container(
                        padding: const EdgeInsets.only(top: 24.0),
                        child: Column(
                          children: <Widget>[
                            Column(
                              children: <Widget>[
                                Text('Affiliation', style: TextStyle(fontSize: 18.0)),
                                Text(snapshot.data.currentAffiliation),
                                Text(''),
                              ],
                            ),
                            Column(
                              children: <Widget>[
                                Text('Position', style: TextStyle(fontSize: 18.0)),
                                Text(snapshot.data.currentPosition),
                                Text(''),
                              ],
                            ),
                            Column(
                              children: <Widget>[
                                Text('Contact', style: TextStyle(fontSize: 18.0)),
                                Text(snapshot.data.contact),
                                Text(''),
                              ],
                            ),
                            Text('Research Interests', style: TextStyle(fontSize: 18.0),),
                            Column(
                              children: <Widget>[
                                Text('Bioinformatics'),
                                Text('Software Development'),
                                Text('Data Engineering')
                              ],
                            ),
                          ],
                        ),
                      ),
                    ],
                  );
                } else {
                  return CircularProgressIndicator();
                }
              },
            ),
          ),
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: () {
            // code here
          },
          child: Icon(Icons.edit),
        ),
      );
    }
  }
}

class FacebookLoginPage extends StatefulWidget {
  FacebookLoginPage({Key key}) : super(key: key);
  @override
  _FacebookLoginState createState() => new _FacebookLoginState();
}

class _FacebookLoginState extends State<FacebookLoginPage> {
  fb.Token token;
  fb.FacebookGraph graph;
  fb.PublicProfile profile;

  HttpClient httpClient = new HttpClient();

  Future<String> authenticate(fb.Token token) async {
    var uri = Uri.http(host,
        '/account/register-by-token/facebook/',
        {"access_token":token.access});
    var request = await httpClient.getUrl(uri);
    var response = await request.close();
    var responseBody = await response.transform(UTF8.decoder).join();
    if (response.statusCode==200) {
      return responseBody;
    } else {
      throw Exception('Failed to authenticate.');
    }
  }

  Future<Null> get_facebook_access_token() async {
    fb.Token _token = await fb.getToken(fb.appId, fb.appSecret);
    fb.FacebookGraph _graph = new fb.FacebookGraph(_token);
    fb.PublicProfile _profile = await _graph.me(["name","picture.type(large)"]);
    token = _token;
    graph = _graph;
    profile = _profile;
  }

  Future<Null> get_jwt_token(fb.Token fbToken) async {
    var responseBody = await authenticate(fbToken);
    var data = json.decode(responseBody);
    jwt_token = data['token'];
    userId = data['user_id'];
  }

  Future<Null> login() async {
    await get_facebook_access_token();
    await get_jwt_token(token);
    if (jwt_token != '') {
      isLoggedIn = true;
      profileCover = profile.cover;
    } else {
      isLoggedIn = false;
    }
    setState(() {});
  }

  @override
  void initState() {
    // TODO: implement initState
    super.initState();
    login();
  }

  @override
  Widget build(BuildContext context) {
    if(isLoggedIn) {
      return Scaffold(
          appBar: AppBar(
            title: Text('Facebook Log In'),
            elevation: 0.0,
          ),
          body: Center(
              child: Container(
                  margin: EdgeInsets.all(16.0),
                  child: Column(
                    children: <Widget>[
                      Container(
                        margin: EdgeInsets.only(bottom: 8.0),
                        child: Text(
                          'Login Succeeded.',
                          style: TextStyle(fontSize: 18.0, fontWeight: FontWeight.bold),
                        ),
                      ),
                      Container(
                        margin: EdgeInsets.only(bottom: 8.0),
                        child: CircleAvatar(
                          backgroundImage: NetworkImage(profile.cover),
                          radius: 42.0,
                        ),
                      ),
                      Container(
                        margin: EdgeInsets.only(bottom: 8.0),
                        child: Text(
                          'Welcome ${profile.name}',
                          style: TextStyle(fontSize: 18.0, fontWeight: FontWeight.bold),
                        ),
                      ),
                      Container(
                        margin: EdgeInsets.only(bottom: 8.0),
                        child: RaisedButton(
                          child: Text(
                              'Your Profile',
                              style: TextStyle(color: Colors.white)),
                          shape: RoundedRectangleBorder(borderRadius: new BorderRadius.circular(18.0)),
                          color: Colors.blue[500],
                          elevation: 0.0,
                          onPressed: () {
                            Navigator.push(
                                context,
                                MaterialPageRoute(
                                    builder: (context) => AccountPage()
                              )
                            );
                          },
                        ),
                      )
                    ],
                  )
              )
          )
      );
    } else {
      return Scaffold(
          appBar: AppBar(
            title: Text('Facebook Log In'),
          ),
          body: Container(
            child: Center(
              child: Text('Oops, something went wrong..'),
            ),
          )
      );

    }
  }
}

import 'dart:async';
import 'dart:io';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_html_view/flutter_html_view.dart';
import 'package:flutter_webview_plugin/flutter_webview_plugin.dart';
import 'package:intl/intl.dart';

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
      title: 'Talent Mobility App',
      theme: ThemeData(
        brightness: Brightness.light,
        primaryColor: Colors.deepOrangeAccent,
        accentColor: Colors.blueGrey,
      ),
      home: Scaffold(
        body: PostsList(),
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
              icon: new Icon(Icons.search),
              onPressed: () {
                Navigator.push(context,
                    MaterialPageRoute(builder: (context) => SearchPostForm()));
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

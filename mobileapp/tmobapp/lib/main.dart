import 'dart:async';
import 'dart:io';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_html_view/flutter_html_view.dart';

void main() => runApp(new MainPage());

class Post {
  final int id;
  final String title;
  final String body;
  final feedImage;

  Post({this.id, this.title, this.body, this.feedImage});

  factory Post.fromJson(Map<String, dynamic> json) {
    return Post(
      id: json['id'],
      title: json['title'],
      body: json['body'],
      feedImage: json['feed_image_thumbnail'],
    );
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
    return parsed['items'].map<Post>((json) => Post.fromJson(json)).toList();
  }

  Future<Null> refreshPostList() async {
    setState((){});
    return null;
  }

  HttpClient http = new HttpClient();

  Future<List<Post>> fetchPost() async {
    var uri = Uri.http('209.97.174.132', '/api/v2/pages',
        {"type":"blog.PostPage", "fields":"feed_image_thumbnail,body"});
    var request = await http.getUrl(uri);
    var response = await request.close();
    var responseBody = await response.transform(UTF8.decoder).join();
    // final response = await http.get('http://209.97.174.132/api/v2/pages?type=blog.PostPage&fields=feed_image_thumbnail,body');
    if (response.statusCode == 200) {
      // setState(() {});
      return parsePosts(responseBody);
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
              return Column(
                children: <Widget>[
                  Card(
                    child: Container(
                        padding: EdgeInsets.all(16.0),
                        child: Column(
                          children: <Widget>[
                            snapshot.data[index].feedImage != null ?
                            Image.network(
                                'http://209.97.174.132${snapshot.data[index].feedImage['url']}'
                            ) : Container(),
                            ListTile(
                              title: Text(
                                '${snapshot.data[index].title}',
                                style: TextStyle(
                                  fontSize: 20.0,
                                ),
                              ),
                              onTap: () {
                                Navigator.push(
                                    context,
                                    MaterialPageRoute(builder:
                                (context)=>DetailPost(post:snapshot.data[index]))
                                );
                              },
                            ),
                          ],
                        ),
                      ),
                    ),
                  ]
              );
            },
          );
        } else {
          return Center(child: CircularProgressIndicator());
        }
      }
    );
    return new Scaffold(
      appBar: AppBar(
        elevation: 1.0,
        title: new Text('Recent Posts'),
        actions: <Widget>[
          new IconButton(
            icon: new Icon(Icons.search),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => SearchPostForm())
              );
            },
          )
        ]
      ),
      body: new RefreshIndicator(
          onRefresh: refreshPostList,
          child: postListFuture,
      ),
      bottomNavigationBar: BottomNavigationBar(
          items: [
            BottomNavigationBarItem(
              icon: Icon(Icons.category),
              title: Text('Categories'),
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.label),
              title: Text('Tags'),
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.people),
              title: Text('Community'),
            )
          ]
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
              Text('${post.title}',
                style: TextStyle(
                    fontSize: 22.0),
              ),
              HtmlView(data: post.body),
            ],
          ),
        )
      ),
      floatingActionButton: FloatingActionButton(
        child: Icon(Icons.format_quote),
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => PostCommentForm())
          );
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

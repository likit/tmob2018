import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() => runApp(new MainPage());

class Post {
  final int userId;
  final int id;
  final String title;
  final String body;

  Post({this.userId, this.id, this.title, this.body});

  factory Post.fromJson(Map<String, dynamic> json) {
    return Post(
      userId: json['userId'],
      id: json['id'],
      title: json['title'],
      body: json['body'],
    );
  }
}

class MainPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Talent Mobility App',
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
    final parsed = json.decode(responseBody).cast<Map<String, dynamic>>();
    return parsed.map<Post>((json) => Post.fromJson(json)).toList();
  }

  Future<Null> refreshPostList() async {
    setState((){});
    return null;
  }

  Future<List<Post>> fetchPost() async {
    final response = await http.get('https://jsonplaceholder.typicode.com/posts');
    if (response.statusCode == 200) {
      setState(() {});
      return parsePosts(response.body);
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
                  ListTile(
                    title: Text(
                        '${snapshot.data[index].title}',
                        style: TextStyle(
                          fontSize: 20.0,
                        ),
                      ),
                    subtitle: Text('lorem posum i am going to hongkong this month, please let me handle this.'),
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (context)=>DetailPost(post: snapshot.data[index])),
                      );
                    }
                  ),
                  Divider(),
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
        title: new Text('Recent Posts'),
      ),
      body: new RefreshIndicator(
          onRefresh: refreshPostList,
          child: postListFuture,
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
        title: Text('Post Page'),
      ),
      body: Container(
        margin: const EdgeInsets.all(16.0),
        child: Column(
          children: <Widget>[
            Text('${post.title}',
              style: TextStyle(
                  fontSize: 18.0),
              ),
            Text('posted by user id = ${post.userId}'),
            RaisedButton(
              child: Text('Back'),
              onPressed: () {
                Navigator.pop(context);
              },
            ),
          ],
        ),
      )
    );
  }
}

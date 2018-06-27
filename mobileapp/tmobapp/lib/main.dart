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

List<Post> parsePosts(String responseBody) {
  final parsed = json.decode(responseBody).cast<Map<String, dynamic>>();
  return parsed.map<Post>((json)=>Post.fromJson(json)).toList();
}

Future<List<Post>> fetchPost(http.Client client) async {
  final response = await client.get(
      'https://jsonplaceholder.typicode.com/posts');
  if (response.statusCode == 200) {
    return compute(parsePosts,response.body);
  }
}

class MainPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Talent Mobility App',
      home: new Scaffold(
        appBar: AppBar(
          title: new Text('Recent Posts'),
        ),
        body: new FutureBuilder<List<Post>>(
          future: fetchPost(http.Client()),
          builder: (context, snapshot) {
            if (snapshot.hasError) print(snapshot.error);
            return snapshot.hasData
                ? PostsList(posts: snapshot.data)
                : Center(child: CircularProgressIndicator());
          },
        ),
      ),
    );
  }
}


class PostsList extends StatelessWidget {
  final List<Post> posts;

  PostsList({Key key, this.posts}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return new ListView.builder(
      itemCount: posts.length,
      itemBuilder: (BuildContext context, index) {
        if (index.isOdd) return new Divider();
        return ListTile(
          title: new Text(posts[index].title),
          subtitle: new Text('User ID: ${posts[index].userId}'),
        );
      },
    );
  }
}

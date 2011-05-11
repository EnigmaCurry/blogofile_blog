<%inherit file="bf_base_template" />
% for posts in month_posts:
<h1>${posts[0].date.strftime("%B %Y")}</h1>
<ul>
  % for post in posts:
  <li><a href="${post.permapath()}">${post.title}</a></li>
  % endfor
</ul>
% endfor

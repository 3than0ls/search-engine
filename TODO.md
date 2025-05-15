# TODO

1) Write report

2) Write optimizations to index by splitting it up into portions

3) Implement merging, but actually. POLYPHASE MERGING

- dump batches of postings, then at the end, polyphase merge them

- then, for searching, split them up into different files a-z to optimize search speed

4) Terms must be sorted alphabetically

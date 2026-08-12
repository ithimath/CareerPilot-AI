import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '@/lib/api'
import { Users, ThumbsUp, MessageSquare, Plus, Tag, Send, ChevronDown, ChevronUp } from 'lucide-react'
import toast from 'react-hot-toast'

function PostCard({ post, onUpvote }: { post: any; onUpvote: (postId: string) => void }) {
  const queryClient = useQueryClient()
  const [showComments, setShowComments] = useState(false)
  const [commentInput, setCommentInput] = useState('')
  const [hasLiked, setHasLiked] = useState(false)

  // Fetch comments for this post when thread expanded
  const { data: commentsData, isLoading: isLoadingComments } = useQuery({
    queryKey: ['postComments', post.id],
    queryFn: () => api.get(`/api/community/posts/${post.id}/comments`).then(r => r.data),
    enabled: showComments,
  })

  // Mutation for adding a comment
  const addCommentMutation = useMutation({
    mutationFn: (text: string) => api.post(`/api/community/posts/${post.id}/comments`, { content: text }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['postComments', post.id] })
      queryClient.invalidateQueries({ queryKey: ['communityPosts'] })
      setCommentInput('')
      toast.success('Comment posted!')
    },
    onError: () => toast.error('Failed to post comment'),
  })

  const handleLike = () => {
    onUpvote(post.id)
    setHasLiked(true)
  }

  const handleCommentSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!commentInput.trim() || addCommentMutation.isPending) return
    addCommentMutation.mutate(commentInput.trim())
  }

  const comments = commentsData?.comments || []

  return (
    <div className="card p-6 space-y-4 shadow-2xs">
      {/* Post Author Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-teal-700 dark:bg-teal-600 text-white rounded-lg flex items-center justify-center text-xs font-extrabold shadow-xs">
            {post.avatar || post.author?.[0] || 'U'}
          </div>
          <div>
            <p className="text-xs font-bold text-app">{post.author}</p>
            <p className="text-[10px] text-secondary font-medium">{post.role} • {post.created_at}</p>
          </div>
        </div>
      </div>

      {/* Post Body */}
      <div>
        <h3 className="font-heading text-lg font-bold text-app mb-1">{post.title}</h3>
        <p className="text-xs text-secondary leading-relaxed whitespace-pre-line font-medium">{post.content}</p>
      </div>

      {/* Post Footer & Controls */}
      <div className="flex items-center justify-between pt-3 border-t border-app flex-wrap gap-2">
        <div className="flex items-center gap-1.5 flex-wrap">
          {post.tags?.map((t: string) => (
            <span key={t} className="badge badge-sand flex items-center gap-1 text-[10px]">
              <Tag className="w-2.5 h-2.5" /> {t}
            </span>
          ))}
        </div>

        <div className="flex items-center gap-3 text-xs text-secondary font-bold">
          {/* Like / Upvote Button */}
          <button
            onClick={handleLike}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-md transition-all ${
              hasLiked
                ? 'bg-teal-50 text-teal-900 border border-teal-200 dark:bg-teal-950/40 dark:text-teal-300 dark:border-teal-800'
                : 'hover:bg-subtle hover:text-teal-700 dark:hover:text-teal-400'
            }`}
          >
            <ThumbsUp className={`w-3.5 h-3.5 ${hasLiked ? 'fill-teal-700 text-teal-700 dark:fill-teal-400 dark:text-teal-400' : ''}`} />
            <span>{post.upvotes || 0} Upvotes</span>
          </button>

          {/* Comments Toggle Button */}
          <button
            onClick={() => setShowComments(!showComments)}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded-md hover:bg-subtle hover:text-teal-700 dark:hover:text-teal-400 transition-all"
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>{post.comments_count || 0} Comments</span>
            {showComments ? <ChevronUp className="w-3 h-3 ml-0.5" /> : <ChevronDown className="w-3 h-3 ml-0.5" />}
          </button>
        </div>
      </div>

      {/* Expandable Comments Section */}
      {showComments && (
        <div className="pt-3 border-t border-app space-y-3 animate-fade-in">
          <p className="text-[11px] font-bold text-secondary uppercase tracking-wider">Discussion Comments</p>

          {/* Comment List */}
          {isLoadingComments ? (
            <p className="text-xs text-secondary italic">Loading comments...</p>
          ) : comments.length === 0 ? (
            <p className="text-xs text-secondary font-medium italic">No comments yet. Share your thoughts below!</p>
          ) : (
            <div className="space-y-2.5 max-h-60 overflow-y-auto pr-1">
              {comments.map((c: any) => (
                <div key={c.id} className="p-3 bg-subtle rounded-xl border border-app text-xs space-y-1">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="w-5 h-5 bg-teal-700 text-white rounded flex items-center justify-center text-[10px] font-bold">
                        {c.avatar || c.author?.[0] || 'C'}
                      </span>
                      <span className="font-bold text-app">{c.author}</span>
                      <span className="text-[10px] text-secondary font-medium">• {c.role}</span>
                    </div>
                    <span className="text-[10px] text-secondary">{c.created_at}</span>
                  </div>
                  <p className="text-secondary font-medium pl-7 leading-relaxed">{c.content}</p>
                </div>
              ))}
            </div>
          )}

          {/* Add Comment Input Form */}
          <form onSubmit={handleCommentSubmit} className="flex items-center gap-2 pt-1">
            <input
              type="text"
              className="input text-xs flex-1"
              placeholder="Add a comment to this discussion..."
              value={commentInput}
              onChange={(e) => setCommentInput(e.target.value)}
            />
            <button
              type="submit"
              disabled={!commentInput.trim() || addCommentMutation.isPending}
              className="btn btn-primary text-xs py-2 px-3 gap-1"
            >
              <span>Comment</span>
              <Send className="w-3 h-3 text-white" />
            </button>
          </form>
        </div>
      )}
    </div>
  )
}

export default function CommunityPage() {
  const queryClient = useQueryClient()
  const [showModal, setShowModal] = useState(false)
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [tagsInput, setTagsInput] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['communityPosts'],
    queryFn: () => api.get('/api/community/posts').then(r => r.data),
  })

  const postMutation = useMutation({
    mutationFn: () => {
      const tags = tagsInput.split(',').map(t => t.trim()).filter(Boolean)
      return api.post('/api/community/posts', { title, content, tags })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['communityPosts'] })
      setShowModal(false)
      setTitle('')
      setContent('')
      setTagsInput('')
      toast.success('Discussion topic published!')
    },
    onError: () => toast.error('Failed to publish post'),
  })

  const upvoteMutation = useMutation({
    mutationFn: (postId: string) => api.post(`/api/community/posts/${postId}/upvote`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['communityPosts'] })
      toast.success('Upvoted topic!')
    },
    onError: () => toast.error('Failed to upvote'),
  })

  const posts = data?.posts || []

  return (
    <div className="space-y-6 max-w-4xl animate-fade-in text-app">
      {/* Header Banner */}
      <div className="card p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xs">
        <div>
          <span className="text-[10px] font-bold text-teal-700 dark:text-teal-400 uppercase tracking-wider block mb-1">Peer & Placement Network</span>
          <div className="flex items-center gap-3">
            <h2 className="font-heading text-3xl font-extrabold text-app">Candidate Network Board</h2>
            <span className="badge badge-emerald flex items-center gap-1">
              <Users className="w-3 h-3 text-teal-700 dark:text-teal-400" /> Verified Peer Network
            </span>
          </div>
          <p className="text-secondary text-xs mt-1 font-medium">
            Connect with candidate peers, discuss project tech stacks, and share interview experiences.
          </p>
        </div>
        <button onClick={() => setShowModal(true)} className="btn btn-primary text-xs gap-2">
          <Plus className="w-4 h-4 text-white" /> Create Topic
        </button>
      </div>

      {/* Posts List */}
      {isLoading ? (
        <div className="space-y-4">
          {[...Array(3)].map((_, i) => <div key={i} className="card h-32 skeleton" />)}
        </div>
      ) : posts.length === 0 ? (
        <div className="card p-12 text-center">
          <Users className="w-8 h-8 text-secondary mx-auto mb-2" />
          <p className="text-xs text-secondary font-medium">No community discussions posted yet. Be the first to start a topic!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {posts.map((post: any) => (
            <PostCard
              key={post.id}
              post={post}
              onUpvote={(postId: string) => upvoteMutation.mutate(postId)}
            />
          ))}
        </div>
      )}

      {/* New Topic Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-xs p-4">
          <div className="card max-w-lg w-full p-6 space-y-4 shadow-lg">
            <h3 className="font-heading text-xl font-bold text-app">Post Discussion Topic</h3>

            <div className="space-y-3">
              <div>
                <label className="text-xs font-bold text-secondary uppercase tracking-wider block mb-1">Topic Title</label>
                <input
                  type="text"
                  className="input text-xs"
                  placeholder="e.g. Collaborators wanted for FastAPI + React project"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                />
              </div>

              <div>
                <label className="text-xs font-bold text-secondary uppercase tracking-wider block mb-1">Content</label>
                <textarea
                  className="input h-32 text-xs"
                  placeholder="Share details or ask a question..."
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                />
              </div>

              <div>
                <label className="text-xs font-bold text-secondary uppercase tracking-wider block mb-1">Tags (Comma-separated)</label>
                <input
                  type="text"
                  className="input text-xs"
                  placeholder="React, Projects, Interview"
                  value={tagsInput}
                  onChange={(e) => setTagsInput(e.target.value)}
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 pt-2 border-t border-app">
              <button onClick={() => setShowModal(false)} className="btn btn-secondary text-xs">Cancel</button>
              <button
                onClick={() => postMutation.mutate()}
                disabled={!title.trim() || !content.trim() || postMutation.isPending}
                className="btn btn-primary text-xs"
              >
                Publish Topic
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

import { useState, useEffect } from 'react'

function Panel({ username }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)  // new — handle errors

  useEffect(() => {
    fetch(`http://localhost:8000/analyze/${username}`)
      .then(res => {
        if (!res.ok) throw new Error("User not found")
        return res.json()
      })
      .then(json => {
        setData(json)
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [])

  return (
    <div style={{
      position: 'fixed',
      bottom: '20px',
      right: '20px',
      background: 'white',
      border: '1px solid #e1e4e8',
      borderRadius: '8px',
      padding: '16px',
      width: '260px',
      boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
      zIndex: 9999,
      fontFamily: 'sans-serif'
    }}>
      <h3 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#24292f' }}>
        ⚡ Repo-Pulse
      </h3>

      {loading && (
        <p style={{ margin: 0, fontSize: '12px', color: '#57606a' }}>
          Analyzing <strong>{username}</strong>...
        </p>
      )}

      {error && (
        <p style={{ margin: 0, fontSize: '12px', color: 'red' }}>
          {error}
        </p>
      )}

      {data && (
        <div style={{ fontSize: '12px', color: '#57606a' }}>
          <p style={{ margin: '0 0 6px 0' }}>
            📦 <strong>{data.stats.public_repos}</strong> repos &nbsp;
            ⭐ <strong>{data.stats.total_stars}</strong> stars
          </p>
          <p style={{ margin: '0 0 6px 0' }}>
            🍴 <strong>{data.stats.total_forks}</strong> forks &nbsp;
            📝 <strong>{data.stats.repos_with_descriptions}</strong> with descriptions
          </p>
          <p style={{ margin: '0 0 4px 0' }}>
            💬 Avg commits/repo: <strong>{data.stats.commit_stats.avg_commits_per_repo}</strong>
          </p>
          <div style={{ marginTop: '8px' }}>
            <p style={{ margin: '0 0 4px 0', fontWeight: 'bold', color: '#24292f' }}>
              Languages:
            </p>
            {Object.entries(data.stats.languages).map(([lang, count]) => (
              <div key={lang}>
                {lang}: <strong>{count} repos</strong>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default Panel
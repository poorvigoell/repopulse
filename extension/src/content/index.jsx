import { createRoot } from 'react-dom/client'
import Panel from './Panel.jsx'

// Extract username from URL
// window.location.pathname on github.com/torvalds/linux = "/torvalds/linux"
// .split('/') = ["", "torvalds", "linux"]
// [1] = "torvalds"
const username = window.location.pathname.split('/')[1]

const container = document.createElement('div')
container.id = 'repo-pulse-root'
document.body.appendChild(container)

createRoot(container).render(<Panel username={username} />)
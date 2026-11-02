import { Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import Landing from './pages/Landing'
import Navigator from './pages/Navigator'
import TestLog from './pages/TestLog'
import Logic from './pages/Logic'
import Credits from './pages/Credits'
import Monitoring from './pages/Monitoring'

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/navigator" element={<Navigator />} />
        <Route path="/navigator/:caseId" element={<Navigator />} />
        <Route path="/navigator/:caseId/:tab" element={<Navigator />} />
        <Route path="/monitoring" element={<Monitoring />} />
        <Route path="/tests" element={<TestLog />} />
        <Route path="/logic" element={<Logic />} />
        <Route path="/logic/:caseId" element={<Logic />} />
        <Route path="/credits" element={<Credits />} />
        <Route path="*" element={<Landing />} />
      </Routes>
    </Layout>
  )
}

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StatusBadge from '@/components/StatusBadge.vue'

describe('StatusBadge', () => {
  it('renders draft status by default', () => {
    const wrapper = mount(StatusBadge)
    expect(wrapper.text()).toBe('草稿')
    expect(wrapper.classes()).toContain('status-draft')
  })

  it('renders pending status correctly', () => {
    const wrapper = mount(StatusBadge, {
      props: { status: 'pending' },
    })
    expect(wrapper.text()).toBe('待审批')
    expect(wrapper.classes()).toContain('status-pending')
  })

  it('renders approved status correctly', () => {
    const wrapper = mount(StatusBadge, {
      props: { status: 'approved' },
    })
    expect(wrapper.text()).toBe('已通过')
    expect(wrapper.classes()).toContain('status-approved')
  })

  it('renders rejected status correctly', () => {
    const wrapper = mount(StatusBadge, {
      props: { status: 'rejected' },
    })
    expect(wrapper.text()).toBe('已拒绝')
    expect(wrapper.classes()).toContain('status-rejected')
  })

  it('has the correct root element class', () => {
    const wrapper = mount(StatusBadge, {
      props: { status: 'approved' },
    })
    expect(wrapper.find('span').exists()).toBe(true)
    expect(wrapper.classes()).toContain('status-badge')
  })
})

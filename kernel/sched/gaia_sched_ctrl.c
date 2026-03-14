// SPDX-License-Identifier: GPL-2.0
/*
 * gaia_sched_ctrl.c
 *
 * Minimal kernel-side workload classification registry for GAIA experiments.
 * This does NOT replace the Linux scheduler. It provides a procfs control plane
 * that can later be consumed by kernel patches, tracepoints, or userspace tools.
 *
 * Interface:
 *   echo "<pid> <class>" > /proc/gaia_sched_ctl
 *   cat /proc/gaia_sched_state
 */

#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/list.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/proc_fs.h>
#include <linux/slab.h>
#include <linux/uaccess.h>

#define GAIA_PROC_CTL   "gaia_sched_ctl"
#define GAIA_PROC_STATE "gaia_sched_state"
#define GAIA_MAX_INPUT  64

enum gaia_workload_class {
    GAIA_WL_BACKGROUND = 0,
    GAIA_WL_INTERACTIVE,
    GAIA_WL_CRITICAL_SERVICE,
    GAIA_WL_POLICY_ENGINE,
    GAIA_WL_SAFETY_MONITOR,
};

struct gaia_pid_class {
    pid_t            pid;
    u32              class_id;
    struct list_head node;
};

static LIST_HEAD(gaia_registry);
static DEFINE_MUTEX(gaia_registry_lock);
static struct proc_dir_entry *gaia_ctl_entry;
static struct proc_dir_entry *gaia_state_entry;

static const char *gaia_class_name(u32 class_id)
{
    switch (class_id) {
    case GAIA_WL_BACKGROUND:       return "background";
    case GAIA_WL_INTERACTIVE:      return "interactive";
    case GAIA_WL_CRITICAL_SERVICE: return "critical_service";
    case GAIA_WL_POLICY_ENGINE:    return "policy_engine";
    case GAIA_WL_SAFETY_MONITOR:   return "safety_monitor";
    default:                       return "unknown";
    }
}

static int gaia_registry_set(pid_t pid, u32 class_id)
{
    struct gaia_pid_class *entry;

    list_for_each_entry(entry, &gaia_registry, node) {
        if (entry->pid == pid) {
            entry->class_id = class_id;
            return 0;
        }
    }

    entry = kzalloc(sizeof(*entry), GFP_KERNEL);
    if (!entry)
        return -ENOMEM;

    entry->pid      = pid;
    entry->class_id = class_id;
    list_add_tail(&entry->node, &gaia_registry);
    return 0;
}

static ssize_t gaia_ctl_write(struct file *file, const char __user *buffer,
                              size_t count, loff_t *ppos)
{
    char  input[GAIA_MAX_INPUT];
    pid_t pid;
    u32   class_id;
    int   ret;

    if (count == 0 || count >= sizeof(input))
        return -EINVAL;

    if (copy_from_user(input, buffer, count))
        return -EFAULT;
    input[count] = '\0';

    ret = sscanf(input, "%d %u", &pid, &class_id);
    if (ret != 2)
        return -EINVAL;

    mutex_lock(&gaia_registry_lock);
    ret = gaia_registry_set(pid, class_id);
    mutex_unlock(&gaia_registry_lock);

    if (ret)
        return ret;

    pr_info("gaia_sched_ctrl: pid=%d class=%u (%s)\n",
            pid, class_id, gaia_class_name(class_id));
    return count;
}

static ssize_t gaia_state_read(struct file *file, char __user *buffer,
                               size_t count, loff_t *ppos)
{
    char                  *kbuf;
    size_t                 len = 0;
    struct gaia_pid_class *entry;
    ssize_t                ret;

    if (*ppos != 0)
        return 0;

    kbuf = kzalloc(PAGE_SIZE, GFP_KERNEL);
    if (!kbuf)
        return -ENOMEM;

    mutex_lock(&gaia_registry_lock);
    list_for_each_entry(entry, &gaia_registry, node) {
        len += scnprintf(kbuf + len, PAGE_SIZE - len,
                         "%d %u %s\n",
                         entry->pid,
                         entry->class_id,
                         gaia_class_name(entry->class_id));
        if (len >= PAGE_SIZE - 64)
            break;
    }
    mutex_unlock(&gaia_registry_lock);

    ret = simple_read_from_buffer(buffer, count, ppos, kbuf, len);
    kfree(kbuf);
    return ret;
}

static const struct proc_ops gaia_ctl_ops = {
    .proc_write = gaia_ctl_write,
};

static const struct proc_ops gaia_state_ops = {
    .proc_read = gaia_state_read,
};

static int __init gaia_sched_ctrl_init(void)
{
    gaia_ctl_entry = proc_create(GAIA_PROC_CTL, 0200, NULL, &gaia_ctl_ops);
    if (!gaia_ctl_entry)
        return -ENOMEM;

    gaia_state_entry = proc_create(GAIA_PROC_STATE, 0444, NULL, &gaia_state_ops);
    if (!gaia_state_entry) {
        proc_remove(gaia_ctl_entry);
        return -ENOMEM;
    }

    pr_info("gaia_sched_ctrl: loaded\n");
    return 0;
}

static void __exit gaia_sched_ctrl_exit(void)
{
    struct gaia_pid_class *entry, *tmp;

    proc_remove(gaia_ctl_entry);
    proc_remove(gaia_state_entry);

    mutex_lock(&gaia_registry_lock);
    list_for_each_entry_safe(entry, tmp, &gaia_registry, node) {
        list_del(&entry->node);
        kfree(entry);
    }
    mutex_unlock(&gaia_registry_lock);

    pr_info("gaia_sched_ctrl: unloaded\n");
}

module_init(gaia_sched_ctrl_init);
module_exit(gaia_sched_ctrl_exit);

MODULE_AUTHOR("Societas AI Research Team");
MODULE_DESCRIPTION("GAIA scheduler control registry");
MODULE_LICENSE("GPL");

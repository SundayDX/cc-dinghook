export interface DingTalkMessage {
  msgtype: 'text' | 'markdown' | 'link' | 'actionCard';
  text?: {
    content: string;
  };
  markdown?: {
    title: string;
    text: string;
  };
  link?: {
    text: string;
    title: string;
    picUrl?: string;
    messageUrl: string;
  };
  actionCard?: {
    text: string;
    title: string;
    hideAvatar?: string;
    btnOrientation?: string;
    btns?: Array<{
      title: string;
      actionURL: string;
    }>;
  };
}

export interface DingTalkResponse {
  errcode: number;
  errmsg: string;
}

export interface HookEventData {
  command?: string;
  exitCode?: number;
  duration?: number;
  timestamp: Date;
  workingDirectory?: string;
  user?: string;
  repository?: string;
  branch?: string;
  commit?: string;
}

export interface NotificationConfig {
  webhookUrl: string;
  secret?: string;
  messageTitle: string;
  includeDuration: boolean;
  includeExitCode: boolean;
}
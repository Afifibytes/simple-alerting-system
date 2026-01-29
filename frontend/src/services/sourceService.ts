import { createService } from './createService';
import type { Source, SourceFormData } from '../types';

export const sourceService = createService<Source, SourceFormData, Partial<SourceFormData>>('/sources', ['active_only', 'search']);

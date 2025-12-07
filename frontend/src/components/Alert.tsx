type AlertProps = {
  title?: string;
  message: string;
};

const Alert = ({ title = 'Error', message }: AlertProps) => {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-red-800 shadow-sm">
      <p className="font-semibold">{title}</p>
      <p className="text-sm">{message}</p>
    </div>
  );
};

export default Alert;

